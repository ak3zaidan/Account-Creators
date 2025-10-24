package main

import (
	"bytes"
	"compress/flate"
	"compress/gzip"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/andybalholm/brotli"
	"github.com/klauspost/compress/zstd"

	fhttp "github.com/bogdanfinn/fhttp"
	tls_client "github.com/bogdanfinn/tls-client"
)

var rng2 *rand.Rand = rand.New(rand.NewSource(time.Now().UnixNano()))
var rngMu2 sync.Mutex

type RequestOptions struct {
	Header   fhttp.Header
	Body     io.Reader
	JSON     any
	FormData url.Values
}

type Response struct {
	*fhttp.Response
	body []byte
}

type ZstdReadCloser struct {
	*zstd.Decoder
}

func (z ZstdReadCloser) Close() error {
	z.Decoder.Close()
	return nil
}

func (r *Response) Bytes() []byte {
	if r.body == nil {
		return nil
	}

	contentEncoding := r.Header.Get("Content-Encoding")

	// First, try to decompress based on the Content-Encoding header
	decompressed, err := r.tryDecompress(contentEncoding)
	if err == nil {
		return decompressed
	}

	// If decompression failed, log the error and return the original body
	return r.body
}

func (r *Response) tryDecompress(encoding string) ([]byte, error) {
	var reader io.ReadCloser
	var err error

	switch encoding {
	case "gzip":
		reader, err = gzip.NewReader(bytes.NewReader(r.body))
	case "deflate":
		reader = flate.NewReader(bytes.NewReader(r.body))
	case "br":
		reader = io.NopCloser(brotli.NewReader(bytes.NewReader(r.body)))
	case "zstd":
		decoder, err := zstd.NewReader(bytes.NewReader(r.body))
		if err != nil {
			return nil, fmt.Errorf("error creating zstd reader: %w", err)
		}
		reader = ZstdReadCloser{decoder}
	case "":
		return r.body, nil // No compression
	default:
		return nil, fmt.Errorf("unknown Content-Encoding: %s", encoding)
	}

	if err != nil {
		return nil, err
	}

	defer reader.Close()

	return io.ReadAll(reader)
}

func (r *Response) JSON() (any, error) {
	var v any
	err := json.Unmarshal(r.body, &v)
	if err != nil {
		return nil, err
	}
	return v, nil
}

func (r *Response) String() string {
	return string(r.Bytes())
}

func GetCookieValue(session tls_client.HttpClient, targetURL, cookieName string) (string, error) {
	parsed, err := url.Parse(targetURL)
	if err != nil {
		return "", fmt.Errorf("failed to parse URL: %w", err)
	}

	cookies := session.GetCookies(parsed)
	for _, c := range cookies {
		if c.Name == cookieName {
			return c.Value, nil
		}
	}

	return "", fmt.Errorf("cookie %q not found", cookieName)
}

func createHeaderOrder(headers fhttp.Header) (map[string]string, []string) {
	masterHeaderOrder := []string{
		"accept",
		"accept-encoding",
		"accept-language",
		"cache-control",
		"content-type",
		"cookie",
		"device_profile_ref_id",
		"device-memory",
		"dnt",
		"downlink",
		"dpr",
		"ect",
		"origin",
		"priority",
		"referer",
		"rtt",
		"save-data",
		"sec-ch-prefers-color-scheme",
		"sec-ch-ua",
		"sec-ch-ua-arch",
		"sec-ch-ua-full-version",
		"sec-ch-ua-mobile",
		"sec-ch-ua-platform",
		"sec-ch-ua-platform-version",
		"sec-fetch-dest",
		"sec-fetch-mode",
		"sec-fetch-site",
		"sec-fetch-user",
		"tenant-id",
		"traceparent",
		"upgrade-insecure-requests",
		"user-agent",
		"viewport-width",
		"wmlspartner",
		"x-xsrf-token",
		"wm_mp",
		"wm_page_url",
		"wm_qos.correlation_id",
		"x-apollo-operation-name",
		"x-enable-server-timing",
		"x-latency-trace",
		"x-o-bu",
		"x-o-ccm",
		"x-o-correlation-id",
		"x-o-gql-query",
		"x-o-mart",
		"x-o-platform",
		"x-o-platform-version",
		"x-o-segment",
	}

	headerMap := make(map[string]string)
	headerOrderKey := make([]string, 0, len(headers))

	// First, process headers in the master order
	for _, key := range masterHeaderOrder {
		for k, v := range headers {
			lowercaseKey := strings.ToLower(k)
			if key == lowercaseKey {
				headerMap[lowercaseKey] = v[0]
				headerOrderKey = append(headerOrderKey, lowercaseKey)
			}
		}
	}

	return headerMap, headerOrderKey
}

func Do(method, endpoint string, client tls_client.HttpClient, userAgent string, r *RequestOptions) (*Response, error) {
	var bodyReader io.Reader

	if r == nil {
		r = &RequestOptions{Header: make(fhttp.Header)}
	}

	if r.JSON != nil {
		jsonData, err := json.Marshal(r.JSON)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal JSON: %w", err)
		}
		bodyReader = bytes.NewReader(jsonData)
	} else if r.FormData != nil {
		formData := r.FormData.Encode()
		bodyReader = strings.NewReader(formData)
	}

	req, err := fhttp.NewRequest(method, endpoint, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	r.Header.Set("user-agent", userAgent)

	rngMu2.Lock()
	defer rngMu2.Unlock()

	additionalHeaders := map[string]string{
		"viewport-width": strconv.Itoa(rng2.Intn(2560-320+1) + 320),
		"device-memory":  []string{"2", "4", "6", "8", "12", "16"}[rng2.Intn(6)],
		"sec-ch-ua-full-version": []string{
			`"133.0.6316.134"`,
			`"133.0.6315.130"`,
			`"132.0.6316.134"`,
			`"131.0.6316.134"`,
		}[rng2.Intn(4)],
	}
	// Randomly decide which headers to include
	for headerName, headerValue := range additionalHeaders {
		if rng2.Intn(2) == 1 {
			r.Header.Set(headerName, headerValue)
		}
	}

	headerMap, headerOrderKey := createHeaderOrder(r.Header)
	req.Header = fhttp.Header{
		fhttp.HeaderOrderKey:  headerOrderKey,
		fhttp.PHeaderOrderKey: {":authority", ":method", ":path", ":scheme"},
	}

	for k, v := range headerMap {
		req.Header.Set(k, v)
	}

	u, err := url.Parse(endpoint)
	if err != nil {
		return nil, fmt.Errorf("failed to parse endpoint URL: %w", err)
	}
	req.Header.Set("host", u.Host)

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	return &Response{Response: resp, body: body}, nil
}
