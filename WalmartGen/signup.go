package main

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/fatih/color"

	tls_client "github.com/bogdanfinn/tls-client"
)

func signup(session tls_client.HttpClient, profile Profile, superCookie string) (string, string, error) {
	maxAttempts := 3
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		phoneNumber, id, err := attemptSignup(session, profile, superCookie)
		if err == nil {
			return phoneNumber, id, nil // Successful signup
		}

		// Cancel rental
		if UseDaisy && id != "" {
			client := NewDaisySMSClient(daisyKey, "wr", "")

			client.CancelRental(id)
		}

		// Check for specific error conditions that warrant a retry
		if isRetryableError(err) {
			if attempt < maxAttempts {
				printRed(fmt.Sprintf("Attempt %d failed: %v\nRetrying...\n", attempt, err))
				time.Sleep(5 * time.Second) // Wait before retrying
			} else {
				return "", id, fmt.Errorf("all %d signup attempts failed. Last error: %v", maxAttempts, err)
			}
		} else {
			// If it's not a retryable error, return immediately
			return "", id, err
		}
	}

	return "", "", fmt.Errorf("unexpected error: reached end of signup function")
}

func isRetryableError(err error) bool {
	if CATCHALL_DOMAIN != "" {
		return false
	}

	if err == nil {
		return false
	}

	errorString := err.Error()

	return strings.Contains(
		errorString, "Error polling for code") ||
		strings.Contains(errorString, "OTP_INVALID") ||
		strings.Contains(errorString, "Walmart code post failed")
}

func attemptSignup(session tls_client.HttpClient, profile Profile, superCookie string) (string, string, error) {
	// Setup
	if profile.Email == "" {
		return "", "", fmt.Errorf("no profile email found")
	}

	var newPassword string = ""

	if strings.Contains(profile.Email, ".com:") {
		parts := strings.SplitN(profile.Email, ":", 2)

		profile.Email = parts[0]
		newPassword = parts[1]
	} else {
		newPassword = password
	}

	var id, number string
	var err error

	if UseDaisy {
		client := NewDaisySMSClient(daisyKey, "wr", "")

		id, number, err = client.RentNumberWithOptions(
			0.0,   // Max price - set to 0 to use default pricing
			nil,   // No specific area codes []string{"503"}
			nil,   // No specific carriers
			"",    // No specific number
			false, // Not a long-term rental
			false, // No auto-renew
		)
	} else {
		client := NewSMSPoolClient(apiKey, "999", "1")

		id, number, err = client.RentNumber()
	}

	if err != nil {
		if strings.Contains(err.Error(), "SERVICE_NOT_AVAILABLE_FOR_COUNTRY") {
			printRed("\n\n----Add credits to sms service")
			os.Exit(1)
		}

		return "", id, fmt.Errorf("error renting number: %v\n", err)
	}

	fmt.Printf("1. Rented number: %s (ID: %s)\n", number, id)
	//number = "7207234212"
	formattedSetupPhone := formatPhoneNumber(number)
	if UseDaisy {
		if len(number) == 11 && number[0] == '1' {
			number = number[1:]
		}
	}
	rawSetupPhone := number

	// Part 1
	signUpResp, err := Do("POST", "https://identity.walmart.com/orchestra/idp/graphql", session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":                  {"application/json"},
			"Accept-Language":         {"en-US"},
			"Accept-encoding":         {"gzip, deflate, br, zstd"},
			"Content-Type":            {"application/json"},
			"Downlink":                {"10"},
			"Dpr":                     {"1"},
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
			"Cookie":                  {superCookie},
		},

		JSON: map[string]any{
			"query": `mutation SignUp($input:SignUpInput!){signUp(input:$input){auth{...AuthFragment}authCode{authCode cid}errors{...ErrorFragment}generateOtpResult{...OtpResultFragment}}}fragment AuthFragment on AuthResult{loginId loginIdType emailId phoneNumber{number countryCode}authCode identityToken}fragment ErrorFragment on IdentitySignUpError{code message}fragment OtpResultFragment on GenerateOTPResult{receiptId otpOperation otpType otherAccountsWithPhone action{alternateOption currentOption nextFactor}}`,
			"variables": map[string]any{
				"input": map[string]any{
					"loginId":                 profile.Email,
					"loginIdType":             "EMAIL",
					"password":                newPassword,
					"firstName":               profile.ShippingFirstName,
					"lastName":                profile.ShippingLastName,
					"marketingEmailsAccepted": false,
					"phoneNumber":             formattedSetupPhone,
					"nonProfilePhoneNumber": map[string]string{
						"number":         rawSetupPhone,
						"countryCode":    "+1",
						"isoCountryCode": "US",
					},
				},
			},
		},
	})

	if err != nil {
		return "", id, fmt.Errorf("walmart sign-up request failed: %w", err)
	}
	if signUpResp.StatusCode != 200 {
		fmt.Println(signUpResp.String())
		return "", id, fmt.Errorf("walmart sign-up failed with status: %s", signUpResp.Status)
	}
	if strings.Contains(strings.ToLower(signUpResp.String()), strings.ToLower("EMAIL_ALREADY_SET")) {
		return "", id, fmt.Errorf("walmart sign-up failed: email already used")
	}
	if strings.Contains(strings.ToLower(signUpResp.String()), strings.ToLower("SOMETHING_WENT_WRONG")) {
		return "", id, fmt.Errorf("walmart sign-up failed: unknown")
	}

	// Part 2
	fmt.Println("2. Waiting for SMS code...")

	var code string

	if UseDaisy {
		client := NewDaisySMSClient(daisyKey, "wr", "")

		code, err = client.PollForCode(id, 30*time.Second)
	} else {
		client := NewSMSPoolClient(apiKey, "999", "1")

		code, err = client.PollForCode(id, 30*time.Second)
	}

	if err != nil {
		return "", id, fmt.Errorf("error polling for code: %v\n", err)
	}

	fmt.Printf("3. Received code: %s\n", code)

	// Part 3
	codePassResp, err := Do("POST", "https://identity.walmart.com/orchestra/idp/graphql", session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":                  {"application/json"},
			"Accept-Language":         {"en-US"},
			"Content-Type":            {"application/json"},
			"Downlink":                {"10"},
			"Dpr":                     {"1"},
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
			"Cookie":                  {superCookie},
		},
		JSON: map[string]any{
			"query": `mutation SignUp($input:SignUpInput!){signUp(input:$input){auth{...AuthFragment}authCode{authCode cid}errors{...ErrorFragment}generateOtpResult{...OtpResultFragment}}}fragment AuthFragment on AuthResult{loginId loginIdType emailId phoneNumber{number countryCode}authCode identityToken}fragment ErrorFragment on IdentitySignUpError{code message}fragment OtpResultFragment on GenerateOTPResult{receiptId otpOperation otpType otherAccountsWithPhone action{alternateOption currentOption nextFactor}}`,
			"variables": map[string]any{
				"input": map[string]any{
					"emailId":                 profile.Email,
					"loginId":                 profile.Email,
					"loginIdType":             "EMAIL",
					"password":                newPassword,
					"firstName":               profile.ShippingFirstName,
					"lastName":                profile.ShippingLastName,
					"marketingEmailsAccepted": false,
					"phoneNumber":             formattedSetupPhone,
					"rememberMe":              true,
					"nonProfilePhoneNumber": map[string]string{
						"number":         rawSetupPhone,
						"countryCode":    "+1",
						"isoCountryCode": "US",
					},
					"stepUpOptions": map[string]any{
						"nonProfilePhoneNumber": map[string]string{
							"number":         rawSetupPhone,
							"countryCode":    "+1",
							"isoCountryCode": "US",
						},
						"otpCode":      code,
						"otpOperation": "OTP_UNREGISTERED_USER_PHONE_VERIFY",
						"phoneNumber":  formattedSetupPhone,
					},
				},
			},
		},
	})

	if err != nil {
		return "", id, fmt.Errorf("walmart code post failed: %w", err)
	}

	if codePassResp.StatusCode != 200 || strings.Contains(strings.ToLower(codePassResp.String()), "bad_request") || strings.Contains(strings.ToLower(codePassResp.String()), strings.ToLower("OTP_INVALID")) {
		return "", id, fmt.Errorf("walmart code post failed with status: %s", codePassResp.Status)
	}

	fmt.Println("4. Final account request")

	// Part 4
	followUpGet, err := Do("GET", "https://www.walmart.com/?action=Create&rm=true", session, universalAgent, &RequestOptions{
		Header: map[string][]string{
			"Accept":             {"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"},
			"Accept-Language":    {"en-US,en;q=0.9"},
			"Downlink":           {"10"},
			"Dpr":                {"1"},
			"Priority":           {"u=1, i"},
			"Referer":            {"https://identity.walmart.com/"},
			"Sec-Ch-Ua":          {secua},
			"Sec-Ch-Ua-Mobile":   {"?0"},
			"Sec-Ch-Ua-Platform": {"\"Windows\""},
			"Sec-Fetch-Dest":     {"empty"},
			"Sec-Fetch-Mode":     {"cors"},
			"Sec-Fetch-Site":     {"same-origin"},
			"Cookie":             {superCookie},
		}},
	)

	if err != nil {
		return "", id, fmt.Errorf("final get failed: %w", err)
	}

	if followUpGet.Status == "200 OK" {
		printGreen("5. Account created! " + profile.Email)

		return rawSetupPhone, id, nil
	} else {
		printRed("6. Failed to create account, status: " + followUpGet.Status)

		return "", id, fmt.Errorf("final get failed with status: %s", followUpGet.Status)
	}
}

func printGreen(text string) {
	green := color.New(color.FgGreen).SprintFunc()
	fmt.Println(green(text))
}

func printRed(text string) {
	red := color.New(color.FgRed).SprintFunc()
	fmt.Println(red(text))
}
