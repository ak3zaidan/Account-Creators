package main

import (
	"encoding/json"
	"fmt"
	"regexp"

	tls_client "github.com/bogdanfinn/tls-client"
	"github.com/bogdanfinn/tls-client/profiles"
)

func updateHashes(config Config) error {
	jar := tls_client.NewCookieJar()

	options := []tls_client.HttpClientOption{
		tls_client.WithTimeoutSeconds(30),
		tls_client.WithClientProfile(profiles.DefaultClientProfile),
		tls_client.WithInsecureSkipVerify(),
		tls_client.WithCookieJar(jar),
		//tls_client.WithProxyUrl(grabProxy()),
		tls_client.WithRandomTLSExtensionOrder(),
	}
	session, err := tls_client.NewHttpClient(tls_client.NewNoopLogger(), options...)
	if err != nil {
		return fmt.Errorf("failed to create new HTTP client: %w", err)
	}

	newPlatformVersion, err := getPlatformVersion(&session)
	platformVersion = newPlatformVersion
	if err != nil {
		return err
	}
	newVersion := Version{
		PlatformVersion: newPlatformVersion,
	}

	err = updateVersion(&config, newVersion)
	if err != nil {
		return err
	}

	return nil
}

func getPlatformVersion(session *tls_client.HttpClient) (string, error) {
	platResp, err := Do("GET", "https://www.walmart.com/", *session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":             {"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"},
			"Accept-Language":    {"en-US,en;q=0.9"},
			"Content-Type":       {"application/json"},
			"Downlink":           {"10"},
			"Dpr":                {"1"},
			"Cookie":             {"a"},
			"Priority":           {"u=0, i"},
			"Sec-Ch-Ua":          {secua},
			"Sec-Ch-Ua-Mobile":   {"?0"},
			"Sec-Ch-Ua-Platform": {"\"Windows\""},
			"Sec-Fetch-Dest":     {"empty"},
			"Sec-Fetch-Mode":     {"cors"},
			"Sec-Fetch-Site":     {"same-origin"},
		}},
	)

	if err != nil {
		return "", fmt.Errorf("error getting main page: %w", err)
	}
	if platResp.StatusCode != 200 {
		return "", fmt.Errorf("error getting main page: %s", platResp.Status)
	}

	bodyString := platResp.String()

	// Find the release-metadata script tag
	metadataRegex := regexp.MustCompile(`<script id="release-metadata" type="application/json"[^>]*>(.*?)</script>`)
	metadataMatch := metadataRegex.FindStringSubmatch(bodyString)
	if len(metadataMatch) < 2 {
		return "", fmt.Errorf("release-metadata script not found")
	}

	// Parse the JSON content
	var metadata struct {
		AppVersion string `json:"appVersion"`
	}
	err = json.Unmarshal([]byte(metadataMatch[1]), &metadata)
	if err != nil {
		return "", fmt.Errorf("error parsing release metadata: %w", err)
	}

	if metadata.AppVersion == "" {
		return "", fmt.Errorf("AppVersion not found in release metadata")
	}

	return metadata.AppVersion, nil
}
