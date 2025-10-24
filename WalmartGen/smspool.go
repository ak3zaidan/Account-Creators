package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"
)

const (
	baseURL      = "https://api.smspool.net"
	pollInterval = 5 * time.Second
	maxRetries   = 20
)

type SMSPoolClient struct {
	APIKey  string
	Service string
	Country string
}

// NewSMSPoolClient creates a new client for the SMS Pool API
func NewSMSPoolClient(apiKey string, service string, country string) *SMSPoolClient {
	return &SMSPoolClient{
		APIKey:  apiKey,
		Service: service,
		Country: country,
	}
}

// RentNumber requests a phone number from SMS Pool
// Returns id, number, error to match the original SMS client interface
func (c *SMSPoolClient) RentNumber() (string, string, error) {
	formValues := map[string]string{
		"key":            c.APIKey,
		"country":        c.Country,
		"service":        c.Service,
		"pricing_option": "0", // Set to 0 if you'd like the cheapest numbers, set to 1 for highest success rate
	}

	form, contentType, err := buildMultipartForm(formValues)
	if err != nil {
		return "", "", fmt.Errorf("failed to build form: %w", err)
	}

	client := &http.Client{}
	req, err := http.NewRequest("POST", baseURL+"/purchase/sms", form)
	if err != nil {
		return "", "", fmt.Errorf("failed to create SMSPool request: %w", err)
	}
	req.Header.Set("Content-Type", contentType)

	resp, err := client.Do(req)
	if err != nil {
		return "", "", fmt.Errorf("SMSPool request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", fmt.Errorf("failed to read SMSPool response: %w", err)
	}

	var response struct {
		Success int    `json:"success"`
		Number  int64  `json:"number"`
		ID      string `json:"order_id"`
		Type    string `json:"type"`
	}

	if err := json.Unmarshal(bodyBytes, &response); err != nil {
		return "", "", fmt.Errorf("failed to parse SMSPool response: %w\nRaw: %s", err, string(bodyBytes))
	}

	if response.Success != 1 {
		return "", "", fmt.Errorf("SMSPool error: %s", response.Type)
	}

	number := fmt.Sprintf("%d", response.Number)
	// Remove country code prefix if it exists
	if len(number) == 11 && number[0] == '1' {
		number = number[1:] // Remove leading '1' if present
	}

	return response.ID, number, nil
}

// PollForCode polls for the SMS code from SMS Pool
// Matches the interface of the original SMS client
func (c *SMSPoolClient) PollForCode(id string, timeout time.Duration) (string, error) {
	deadline := time.Now().Add(timeout)
	retry := 0

	for time.Now().Before(deadline) {
		if retry >= maxRetries {
			return "", fmt.Errorf("reached maximum retries waiting for SMS code")
		}

		form, contentType, err := buildSecMultipartForm(id, c.APIKey)
		if err != nil {
			return "", err
		}

		client := &http.Client{}
		req, err := http.NewRequest("POST", baseURL+"/sms/check", form)
		if err != nil {
			return "", fmt.Errorf("failed to create SMSPool request: %w", err)
		}
		req.Header.Set("Content-Type", contentType)

		resp, err := client.Do(req)
		if err != nil {
			return "", fmt.Errorf("SMSPool request failed: %w", err)
		}

		bodyBytes, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			return "", fmt.Errorf("failed to read SMSPool response: %w", err)
		}

		// Parse the response based on the new API endpoint format
		var checkResponse struct {
			Status     int    `json:"status"`
			SMS        string `json:"sms"`
			FullSMS    string `json:"full_sms"`
			Resend     int    `json:"resend"`
			Expiration int64  `json:"expiration"`
			TimeLeft   int    `json:"time_left"`
			Error      string `json:"error"`
		}

		if err := json.Unmarshal(bodyBytes, &checkResponse); err != nil {
			return "", fmt.Errorf("failed to parse SMSPool response: %w\nRaw: %s", err, string(bodyBytes))
		}

		// Check if there's an error
		if checkResponse.Error != "" {
			return "", fmt.Errorf("SMSPool API error: %s", checkResponse.Error)
		}

		// Status 3 means completed with SMS code
		if checkResponse.Status == 3 && checkResponse.SMS != "" {
			return checkResponse.SMS, nil
		}

		// Status 1 means pending
		if checkResponse.Status == 1 {
			fmt.Println("Retrying")

			// Sleep before retrying
			time.Sleep(pollInterval)
			retry++
		}

	}
	return "", fmt.Errorf("no SMS code found for order ID: %s", id)
}

func formatPhoneNumber(number string) string {
	if len(number) != 10 && len(number) != 11 {
		return number // Return as is if it's not a 10 or 11 digit number
	}

	if len(number) == 11 && number[0] == '1' {
		number = number[1:] // Remove leading '1' if present
	}

	return fmt.Sprintf("(%s) %s-%s", number[:3], number[3:6], number[6:])
}

// Helper functions for building multipart forms
func buildMultipartForm(formValues map[string]string) (*bytes.Buffer, string, error) {
	form := new(bytes.Buffer)
	writer := multipart.NewWriter(form)

	// Add form fields from map
	for fieldName, fieldValue := range formValues {
		formField, err := writer.CreateFormField(fieldName)
		if err != nil {
			return nil, "", fmt.Errorf("failed to create form field for %s: %w", fieldName, err)
		}

		if _, err = formField.Write([]byte(fieldValue)); err != nil {
			return nil, "", fmt.Errorf("failed to write %s: %w", fieldName, err)
		}
	}

	// Close the writer to finalize the form
	if err := writer.Close(); err != nil {
		return nil, "", fmt.Errorf("failed to close multipart writer: %w", err)
	}

	return form, writer.FormDataContentType(), nil
}

func buildSecMultipartForm(orderID string, apiKey string) (*bytes.Buffer, string, error) {
	form := new(bytes.Buffer)
	writer := multipart.NewWriter(form)

	// Add orderid field
	err := addFormField(writer, "orderid", orderID)
	if err != nil {
		return nil, "", err
	}

	// Add key field
	err = addFormField(writer, "key", apiKey)
	if err != nil {
		return nil, "", err
	}

	// Close the writer
	err = writer.Close()
	if err != nil {
		return nil, "", fmt.Errorf("failed to close form writer: %w", err)
	}

	return form, writer.FormDataContentType(), nil
}

func addFormField(writer *multipart.Writer, fieldName, fieldValue string) error {
	formField, err := writer.CreateFormField(fieldName)
	if err != nil {
		return fmt.Errorf("failed to create form field for %s: %w", fieldName, err)
	}

	_, err = formField.Write([]byte(fieldValue))
	if err != nil {
		return fmt.Errorf("failed to write %s: %w", fieldName, err)
	}

	return nil
}
