package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const (
	baseDaisyURL = "https://daisysms.com/stubs/handler_api.php"
)

// DaisySMSClient represents a client for the DaisySMS API
type DaisySMSClient struct {
	APIKey  string
	Service string
	Country string // Optional field for country code
}

// ServiceInfo represents information about a service
type ServiceInfo struct {
	Price         float64 `json:"price"`
	Count         int     `json:"count"`
	MultipleCode  bool    `json:"multipleCode"`
	LTRPrice      float64 `json:"ltrPrice,omitempty"`
	LTRAvailable  bool    `json:"ltrAvailable,omitempty"`
	CountryNumber int     `json:"countryNumber"`
}

// NewDaisySMSClient creates a new client for the DaisySMS API
func NewDaisySMSClient(apiKey string, service string, country string) *DaisySMSClient {
	return &DaisySMSClient{
		APIKey:  apiKey,
		Service: service,
		Country: country,
	}
}

// GetBalance returns the current balance of the account
func (c *DaisySMSClient) GetBalance() (float64, error) {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getBalance")

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return 0, fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return 0, fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)
	if strings.HasPrefix(response, "BAD_KEY") {
		return 0, fmt.Errorf("API key invalid")
	}

	if !strings.HasPrefix(response, "ACCESS_BALANCE:") {
		return 0, fmt.Errorf("unexpected response format: %s", response)
	}

	// Extract balance from format "ACCESS_BALANCE:50.30"
	balanceStr := strings.TrimPrefix(response, "ACCESS_BALANCE:")
	balance, err := strconv.ParseFloat(balanceStr, 64)
	if err != nil {
		return 0, fmt.Errorf("failed to parse balance: %w", err)
	}

	return balance, nil
}

// RentNumber requests a phone number from DaisySMS
// Returns id, number, error
func (c *DaisySMSClient) RentNumber(options map[string]string) (string, string, error) {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getNumber")
	params.Add("service", c.Service)

	// Add optional parameters
	for key, value := range options {
		params.Add(key, value)
	}

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return "", "", fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)

	// Handle error responses
	switch {
	case response == "NO_NUMBERS":
		return "", "", fmt.Errorf("no numbers available")
	case response == "NO_MONEY":
		return "", "", fmt.Errorf("not enough balance")
	case response == "MAX_PRICE_EXCEEDED":
		return "", "", fmt.Errorf("max price exceeded")
	case response == "TOO_MANY_ACTIVE_RENTALS":
		return "", "", fmt.Errorf("too many active rentals")
	case response == "BAD_KEY":
		return "", "", fmt.Errorf("API key invalid")
	case !strings.HasPrefix(response, "ACCESS_NUMBER:"):
		return "", "", fmt.Errorf("unexpected response format: %s", response)
	}

	// Extract ID and number from format "ACCESS_NUMBER:999999:13476711222"
	parts := strings.Split(strings.TrimPrefix(response, "ACCESS_NUMBER:"), ":")
	if len(parts) != 2 {
		return "", "", fmt.Errorf("unexpected response format: %s", response)
	}

	id := parts[0]
	number := parts[1]

	return id, number, nil
}

// RentNumberWithOptions requests a phone number with various options like area codes, carriers, etc.
func (c *DaisySMSClient) RentNumberWithOptions(maxPrice float64, areas []string, carriers []string, number string, isLTR bool, autoRenew bool) (string, string, error) {
	options := make(map[string]string)

	if maxPrice > 0 {
		options["max_price"] = fmt.Sprintf("%.2f", maxPrice)
	}

	if len(areas) > 0 {
		options["areas"] = strings.Join(areas, ",")
	}

	if len(carriers) > 0 {
		options["carriers"] = strings.Join(carriers, ",")
	}

	if number != "" {
		options["number"] = number
	}

	if isLTR {
		options["ltr"] = "1"

		if autoRenew {
			options["auto_renew"] = "1"
		}
	}

	return c.RentNumber(options)
}

// PollForCode polls for the SMS code from DaisySMS
func (c *DaisySMSClient) PollForCode(id string, timeout time.Duration) (string, error) {
	deadline := time.Now().Add(timeout)
	retry := 0

	for time.Now().Before(deadline) {
		if retry >= maxRetries {
			return "", fmt.Errorf("reached maximum retries waiting for SMS code")
		}

		code, status, err := c.GetActivationStatus(id)
		if err != nil {
			return "", err
		}

		switch status {
		case "STATUS_OK":
			return code, nil
		case "STATUS_WAIT_CODE":
			// Still waiting for the code
			time.Sleep(pollInterval)
			retry++
		case "STATUS_CANCEL":
			return "", fmt.Errorf("rental was cancelled")
		default:
			return "", fmt.Errorf("unexpected status: %s", status)
		}
	}

	return "", fmt.Errorf("timed out waiting for SMS code")
}

// GetActivationStatus checks the status of an activation
func (c *DaisySMSClient) GetActivationStatus(id string) (string, string, error) {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getStatus")
	params.Add("id", id)

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return "", "", fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)

	if response == "NO_ACTIVATION" {
		return "", "", fmt.Errorf("activation not found")
	}

	// Handle different status responses
	if strings.HasPrefix(response, "STATUS_OK:") {
		code := strings.TrimPrefix(response, "STATUS_OK:")
		return code, "STATUS_OK", nil
	} else if response == "STATUS_WAIT_CODE" {
		fmt.Println("Retrying")

		return "", "STATUS_WAIT_CODE", nil
	} else if response == "STATUS_CANCEL" {
		return "", "STATUS_CANCEL", nil
	}

	return "", "", fmt.Errorf("unexpected response format: %s", response)
}

// MarkRentalAsDone marks a rental as done
func (c *DaisySMSClient) MarkRentalAsDone(id string) error {
	return c.SetActivationStatus(id, "6")
}

// CancelRental cancels a rental
func (c *DaisySMSClient) CancelRental(id string) error {
	return c.SetActivationStatus(id, "8")
}

// SetActivationStatus sets the status of an activation
func (c *DaisySMSClient) SetActivationStatus(id, status string) error {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "setStatus")
	params.Add("id", id)
	params.Add("status", status)

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)

	switch response {
	case "ACCESS_ACTIVATION", "ACCESS_CANCEL":
		return nil
	case "NO_ACTIVATION":
		return fmt.Errorf("activation not found")
	case "ACCESS_READY":
		return fmt.Errorf("already received the code or rental missing")
	default:
		return fmt.Errorf("unexpected response: %s", response)
	}
}

// SetAutoRenew sets the auto renew value for a long-term rental
func (c *DaisySMSClient) SetAutoRenew(id string, autoRenew bool) error {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "setAutoRenew")
	params.Add("id", id)

	value := "false"
	if autoRenew {
		value = "true"
	}
	params.Add("value", value)

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)

	if response != "OK" {
		return fmt.Errorf("unexpected response: %s", response)
	}

	return nil
}

// RequestExtraActivation requests an additional message for a previous activation
func (c *DaisySMSClient) RequestExtraActivation(previousActivationID string) error {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getExtraActivation")
	params.Add("activationId", previousActivationID)

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	response := string(bodyBytes)

	switch response {
	case "ACCESS_CANCEL":
		return nil
	case "ACCESS_READY":
		return fmt.Errorf("rental missing or already got the code")
	default:
		return fmt.Errorf("unexpected response: %s", response)
	}
}

// GetServicePrices gets the list of services with prices
func (c *DaisySMSClient) GetServicePrices() (map[string]map[string]ServiceInfo, error) {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getPricesVerification")

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return nil, fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	var services map[string]map[string]ServiceInfo
	if err := json.Unmarshal(bodyBytes, &services); err != nil {
		return nil, fmt.Errorf("failed to parse services response: %w", err)
	}

	return services, nil
}

// GetCountryPrices gets the list of countries with services and prices
func (c *DaisySMSClient) GetCountryPrices() (map[string]map[string]ServiceInfo, error) {
	params := url.Values{}
	params.Add("api_key", c.APIKey)
	params.Add("action", "getPrices")

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseDaisyURL, params.Encode()))
	if err != nil {
		return nil, fmt.Errorf("DaisySMS request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read DaisySMS response: %w", err)
	}

	var countries map[string]map[string]ServiceInfo
	if err := json.Unmarshal(bodyBytes, &countries); err != nil {
		return nil, fmt.Errorf("failed to parse countries response: %w", err)
	}

	return countries, nil
}
