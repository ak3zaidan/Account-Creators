package main

import (
	"fmt"
	"net"
	"net/url"
	"strings"
	"time"

	fhttp "github.com/bogdanfinn/fhttp"
	tls_client "github.com/bogdanfinn/tls-client"
	"github.com/bogdanfinn/tls-client/profiles"
)

var superCookie string

func clearAllCookies(session tls_client.HttpClient) {
	jar := tls_client.NewCookieJar(tls_client.WithAllowEmptyCookies())
	session.SetCookieJar(jar)
}

func setup(proxy string, profile Profile) error {
	jar := tls_client.NewCookieJar(tls_client.WithAllowEmptyCookies())
	dialer := net.Dialer{
		Timeout:   30 * time.Second,
		KeepAlive: 30 * time.Second,
	}
	idleTimeout := 100 * time.Millisecond

	session, err := tls_client.NewHttpClient(
		tls_client.NewNoopLogger(),
		tls_client.WithTimeoutSeconds(30),
		tls_client.WithClientProfile(profiles.DefaultClientProfile),
		tls_client.WithInsecureSkipVerify(),
		tls_client.WithCookieJar(jar),
		tls_client.WithDialer(dialer),
		tls_client.WithTransportOptions(&tls_client.TransportOptions{
			DisableKeepAlives: true,
			IdleConnTimeout:   &idleTimeout,
		}),
		tls_client.WithProxyUrl(proxy),
		tls_client.WithRandomTLSExtensionOrder(),
	)

	if err != nil {
		return fmt.Errorf("failed to create new HTTP client: %w", err)
	}

	xptwjVal, err := walmartGifWatcherForContentViewingAndOtherThingsSometimes2(session)
	if err != nil {
		return err
	}
	bstcVal, err := walmartGifWatcherForContentViewingAndOtherThingsSometimes(session)
	if err != nil {
		return err
	}

	clearAllCookies(session)

	superCookie = fmt.Sprintf("_pxvid=a; _px3=a; AID=a;  xpth=a; xpa=a; _pxde=a; bstc=%s;%s", bstcVal, xptwjVal)

	phoneNumber, _, err := signup(session, profile, superCookie)

	if err != nil {
		if include_created {
			if strings.Contains(err.Error(), "email already used") {
				var newPassword string = ""

				if strings.Contains(profile.Email, ".com:") {
					parts := strings.SplitN(profile.Email, ":", 2)

					profile.Email = parts[0]
					newPassword = parts[1]
				} else {
					newPassword = password
				}

				AddLine([]string{profile.Email, newPassword, profile.ShippingFirstName + " " + profile.ShippingLastName, phoneNumber})
			}
		}

		return fmt.Errorf("%w", err)
	}

	walmartAffilUrl, _ := url.Parse("https://.walmart.com")
	xsrfCookie := &fhttp.Cookie{
		Name:   "XSRF-TOKEN",
		Value:  "~",
		Domain: ".www.walmart.com",
		Path:   "/",
	}

	session.SetCookies(walmartAffilUrl, []*fhttp.Cookie{xsrfCookie})

	var newPassword string = ""

	if strings.Contains(profile.Email, ".com:") {
		parts := strings.SplitN(profile.Email, ":", 2)

		profile.Email = parts[0]
		newPassword = parts[1]
	} else {
		newPassword = password
	}

	AddLine([]string{profile.Email, newPassword, profile.ShippingFirstName + " " + profile.ShippingLastName, phoneNumber})

	return nil
}

func walmartGifWatcherForContentViewingAndOtherThingsSometimes2(session tls_client.HttpClient) (string, error) {
	gifResp, err := Do("GET", "https://identity.walmart.com/account/login?redirect_uri=https%3A%2F%2Fwww.walmart.com%2Faccount%2FverifyToken&scope=openid+email+offline_access&tenant_id=elh9ie", session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":             {"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"},
			"Accept-Language":    {"en-US,en;q=0.9"},
			"Accept-encoding":    {"gzip, deflate, br"},
			"Referer":            {"https://www.walmart.com/"},
			"Sec-Ch-Ua":          {secua},
			"Sec-Ch-Ua-Mobile":   {"?0"},
			"Sec-Ch-Ua-Platform": {"\"Windows\""},
			"Sec-Fetch-Dest":     {"document"},
			"Sec-Fetch-Mode":     {"navigate"},
			"Sec-Fetch-Site":     {"same-site"},
		},
	})
	if err != nil {
		return "", err
	}
	if gifResp.StatusCode != 200 {
		return "", fmt.Errorf("Cookie grab status mismatch %d", gifResp.StatusCode)
	}
	var Cookies string
	for _, c := range gifResp.Response.Cookies() {
		if c.Value != "" {
			Cookies += fmt.Sprintf("%s=%s;", c.Name, c.Value)
		}
	}
	return Cookies, nil
}

func walmartGifWatcherForContentViewingAndOtherThingsSometimes(session tls_client.HttpClient) (string, error) {
	gifResp, err := Do("GET", "https://beacon.walmart.com/rum.gif", session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":                  {"*/*"},
			"Accept-Language":         {"en-US"},
			"Accept-encoding":         {"gzip, deflate, br, zstd"},
			"Origin":                  {"https://identity.walmart.com"},
			"Priority":                {"u=1, i"},
			"Referer":                 {"https://identity.walmart.com/account/signup"},
			"Sec-Ch-Ua":               {secua},
			"Sec-Ch-Ua-Mobile":        {"?0"},
			"Sec-Ch-Ua-Platform":      {"\"Windows\""},
			"Sec-Fetch-Dest":          {"empty"},
			"Sec-Fetch-Mode":          {"cors"},
			"Sec-Fetch-Site":          {"same-origin"},
			"Tenant-Id":               {"elh9ie"},
			"X-Apollo-Operation-Name": {"SignUp"},
			"X-O-Platform-Version":    {platformVersion},
			"X-O-Segment":             {"oaoh"},
		},
	})
	if err != nil {
		return "", err
	}
	for _, c := range gifResp.Response.Cookies() {
		if c.Name == "bstc" {
			return c.Value, nil
		}
	}
	return "", fmt.Errorf("No bstc found (means popmart wont drop for the next 2 blue moons)")
}
