package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/Johnw7789/Go-iClient/icloud"
)

// Config holds the configuration variables
type Config struct {
	ICloudEmail    string
	ICloudPassword string
	CreateCount    int
	FetchExisting  bool
}

type RateLimiter struct {
	batchStartTime time.Time
	batchCount     int
	maxPerBatch    int
	batchDuration  time.Duration
	delayBetween   time.Duration
}

// 5 emails every 30 minutes, with 30 seconds between each email
func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		maxPerBatch:    5,                // 5 emails per batch
		batchDuration:  61 * time.Minute, // 61 minutes between batches
		delayBetween:   30 * time.Second, // 30 seconds between individual emails
		batchStartTime: time.Now(),
	}
}

// Wait implements the rate limiting logic: 5 per 30 minutes with 30s delays between each
func (rl *RateLimiter) Wait() {
	now := time.Now()

	// If this is a new batch (first request or 30 minutes have passed)
	if rl.batchCount == 0 || now.Sub(rl.batchStartTime) >= rl.batchDuration {
		// Reset for new batch
		rl.batchCount = 0
		rl.batchStartTime = now
		fmt.Printf("Starting new batch of %d emails...\n", rl.maxPerBatch)
	}

	// If we've hit the batch limit, wait for the full 30 minutes
	if rl.batchCount >= rl.maxPerBatch {
		timeInBatch := now.Sub(rl.batchStartTime)
		waitTime := rl.batchDuration - timeInBatch

		if waitTime > 0 {
			fmt.Printf("Batch limit reached (%d/%d). Waiting %v for next batch...\n",
				rl.batchCount, rl.maxPerBatch, waitTime.Round(time.Second))
			time.Sleep(waitTime)
		}

		// Reset for new batch
		rl.batchCount = 0
		rl.batchStartTime = time.Now()
		fmt.Printf("Starting new batch of %d emails...\n", rl.maxPerBatch)
	}

	// Add delay between individual requests (except for the first one in a batch)
	if rl.batchCount > 0 {
		fmt.Printf("Waiting %v before next email in batch...\n", rl.delayBetween)
		time.Sleep(rl.delayBetween)
	}

	rl.batchCount++

	// Show progress within batch
	fmt.Printf("Email %d/%d in current batch\n", rl.batchCount, rl.maxPerBatch)
}

// loadConfig loads configuration from environment variables or prompts user
func loadConfig() Config {
	config := Config{}

	// Try to load from environment variables first
	config.ICloudEmail = os.Getenv("ICLOUD_EMAIL")
	config.ICloudPassword = os.Getenv("ICLOUD_PASSWORD")
	createCountStr := os.Getenv("CREATE_COUNT")
	fetchExistingStr := os.Getenv("FETCH_EXISTING")

	reader := bufio.NewReader(os.Stdin)

	// Prompt for email if not set
	if config.ICloudEmail == "" {
		fmt.Print("Enter iCloud email: ")
		email, _ := reader.ReadString('\n')
		config.ICloudEmail = strings.TrimSpace(email)
	}

	// Prompt for password if not set
	if config.ICloudPassword == "" {
		fmt.Print("Enter iCloud password: ")
		password, _ := reader.ReadString('\n')
		config.ICloudPassword = strings.TrimSpace(password)
	}

	// Prompt for fetch existing option if not set
	if fetchExistingStr == "" {
		fmt.Print("Do you want to fetch existing HME addresses? (y/n): ")
		fetchStr, _ := reader.ReadString('\n')
		fetchExistingStr = strings.TrimSpace(fetchStr)
	}
	config.FetchExisting = strings.ToLower(fetchExistingStr) == "y" || strings.ToLower(fetchExistingStr) == "yes"

	// Only ask for create count if user doesn't just want to fetch existing
	if !config.FetchExisting || createCountStr != "" {
		// Prompt for create count if not set
		if createCountStr == "" {
			fmt.Print("Enter number of HME addresses to create (0 to skip creation): ")
			countStr, _ := reader.ReadString('\n')
			createCountStr = strings.TrimSpace(countStr)
		}

		count, err := strconv.Atoi(createCountStr)
		if err != nil || count < 0 {
			log.Fatal("Invalid create count. Please enter a non-negative number.")
		}
		config.CreateCount = count
	}

	return config
}

// authenticateICloud handles the iCloud authentication process
func authenticateICloud(email, password string) (*icloud.Client, error) {
	fmt.Println("Initializing iCloud client...")

	// Create a new iClient with account credentials
	iclient, err := icloud.NewClient(email, password, false)
	if err != nil {
		return nil, fmt.Errorf("failed to create iCloud client: %v", err)
	}

	fmt.Println("Starting authentication process...")

	// Channel to receive authentication result
	authDone := make(chan error, 1)

	// Start authentication in a goroutine
	go func() {
		err := iclient.Login()
		authDone <- err
	}()

	// Prompt user for OTP
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Enter OTP code: ")
	otpInput, _ := reader.ReadString('\n')
	otpInput = strings.TrimSpace(otpInput)

	// Send OTP to the client
	iclient.OtpChannel <- otpInput

	// Wait for authentication to complete
	if err := <-authDone; err != nil {
		return nil, fmt.Errorf("authentication failed: %v", err)
	}

	fmt.Println("Authentication successful!")
	return iclient, nil
}

// logCreatedEmail appends the created email to the created.csv file
func logCreatedEmail(email, label, note string) error {
	fileName := "created.csv"

	// Check if file exists
	_, err := os.Stat(fileName)
	newFile := os.IsNotExist(err)

	// Open file for append or create
	file, err := os.OpenFile(fileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()

	// If new file, write CSV header
	if newFile {
		if _, err := file.WriteString("Timestamp,Email,Label,Note\n"); err != nil {
			return err
		}
	}

	// Format as CSV
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	logEntry := fmt.Sprintf("%s,%s,%s,%s\n", timestamp, email, label, note)

	_, err = file.WriteString(logEntry)
	return err
}

// fetchExistingHMEAddresses retrieves and exports all existing HME addresses to CSV
func fetchExistingHMEAddresses(iclient *icloud.Client) error {
	fmt.Println("Fetching existing Hide My Email addresses...")

	emails, err := iclient.RetrieveHMEList()
	if err != nil {
		return fmt.Errorf("failed to retrieve HME list: %v", err)
	}

	if len(emails) == 0 {
		fmt.Println("No existing Hide My Email addresses found.")
		return nil
	}

	fmt.Printf("Found %d existing Hide My Email addresses.\n\n", len(emails))

	// Create or truncate CSV file
	file, err := os.Create("existing.csv")
	if err != nil {
		return fmt.Errorf("failed to create CSV file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header row
	if err := writer.Write([]string{"Email", "Label", "Note", "Status", "AnonymousID", "Created"}); err != nil {
		return fmt.Errorf("failed to write CSV header: %v", err)
	}

	// Write each email row
	for _, email := range emails {
		status := "Active"
		if !email.IsActive {
			status = "Inactive"
		}

		record := []string{
			email.Hme,
			email.Label,
			email.Note,
			status,
			email.AnonymousID,
			fmt.Sprintf("%d", email.CreateTimestamp),
		}

		if err := writer.Write(record); err != nil {
			log.Printf("Failed to write record for %s: %v", email.Hme, err)
		}
	}

	fmt.Println("All existing HME addresses have been saved to 'existing.csv'")
	return nil
}

// createHMEAddresses creates the specified number of HME addresses
func createHMEAddresses(iclient *icloud.Client, count int) error {
	if count == 0 {
		fmt.Println("Skipping HME creation (count = 0)")
		return nil
	}

	rateLimiter := NewRateLimiter()

	fmt.Printf("Creating %d Hide My Email addresses...\n", count)

	for i := 1; i <= count; i++ {
		// Apply rate limiting
		rateLimiter.Wait()

		label := fmt.Sprintf("HME_%d", i)
		note := fmt.Sprintf("Generated HME address #%d", i)

		fmt.Printf("Creating HME address %d/%d...", i, count)

		// Generate HME email
		emailAddress, err := iclient.ReserveHME(label, note)
		if err != nil {
			fmt.Printf(" FAILED\n")
			log.Printf("Failed to create HME address %d: %v", i, err)
			continue
		}

		fmt.Printf(" SUCCESS: %s\n", emailAddress)

		// Log the created email
		if err := logCreatedEmail(emailAddress, label, note); err != nil {
			log.Printf("Failed to log email to file: %v", err)
		}
	}

	return nil
}

func main() {
	fmt.Println("=== iCloud Hide My Email Generator ===")

	// Load configuration
	config := loadConfig()

	// Authenticate with iCloud
	iclient, err := authenticateICloud(config.ICloudEmail, config.ICloudPassword)
	if err != nil {
		log.Fatalf("Authentication error: %v", err)
	}

	// Fetch existing HME addresses if requested
	if config.FetchExisting {
		if err := fetchExistingHMEAddresses(iclient); err != nil {
			log.Printf("Error fetching existing HME addresses: %v", err)
		}
	}

	// Create new HME addresses if requested
	if config.CreateCount > 0 {
		if err := createHMEAddresses(iclient, config.CreateCount); err != nil {
			log.Fatalf("Error creating HME addresses: %v", err)
		}
	}

	fmt.Println("\n=== Process Complete ===")
	if config.FetchExisting {
		fmt.Println("Check 'existing.txt' for a log of all existing email addresses.")
	}
	if config.CreateCount > 0 {
		fmt.Println("Check 'created.txt' for a log of newly created email addresses.")
	}
}
