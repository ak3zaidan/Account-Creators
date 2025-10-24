package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"
)

var include_created bool = true

var numWorkers int = 2

// Leave thie empty to use emails from "EmailsToUse.txt"

var CATCHALL_DOMAIN string = ""

// This number only applies if using a catchall domain

var CREATE_COUNT int = 20

//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

var secua = `"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"`
var universalAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

var platformVersion string
var apiKey string
var daisyKey string
var password string
var UseDaisy bool

var successCount int = 0

var (
	file   *os.File
	writer *csv.Writer
	mu     sync.Mutex
)

func InitializeCSV(filename string) error {
	var err error
	file, err = os.OpenFile(filename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return fmt.Errorf("error opening file: %w", err)
	}
	writer = csv.NewWriter(file)

	// Check if the file is empty
	fileInfo, err := file.Stat()
	if err != nil {
		return fmt.Errorf("error getting file info: %w", err)
	}

	// Write header only if the file is empty
	if fileInfo.Size() == 0 {
		headers := []string{"Email", "Password", "Name", "Phone Number"}
		if err := writer.Write(headers); err != nil {
			return fmt.Errorf("error writing headers to CSV: %w", err)
		}
		writer.Flush()
		if err := writer.Error(); err != nil {
			return fmt.Errorf("error flushing headers to CSV: %w", err)
		}
	}

	return nil
}

func AddLine(record []string) error {
	mu.Lock()
	defer mu.Unlock()

	if writer == nil {
		return fmt.Errorf("CSV writer not initialized")
	}

	if err := writer.Write(record); err != nil {
		return fmt.Errorf("error writing record to CSV: %w", err)
	}
	writer.Flush()
	return writer.Error()
}

func CloseCSV() error {
	mu.Lock()
	defer mu.Unlock()

	if writer != nil {
		writer.Flush()
	}
	if file != nil {
		return file.Close()
	}
	return nil
}

func main() {
	InitializeCSV("generatedAccounts.csv")
	proxies = loadProxies()
	proxyIndex = 0

	config, err := loadConfig()
	if err != nil {
		fmt.Println("Error reading config:", err)
		return
	}

	err = updateHashes(config)
	if err != nil {
		fmt.Println("Error updating hashes:", err)
		return
	}

	apiKey = config.SMSApiKey
	daisyKey = config.DaisyApiKey
	password = config.Password
	UseDaisy = config.UseDaisy

	if CATCHALL_DOMAIN == "" {
		err = ReadProfiles()

		if err != nil {
			printRed(fmt.Sprintf("Error reading profiles: %v", err))
			return
		}
	} else {
		accountProfiles = []Profile{}

		for range CREATE_COUNT {
			profile := Profile{
				Email:             generateUsername(),
				ShippingFirstName: randomFirstName(),
				ShippingLastName:  randomLastName(),
			}

			accountProfiles = append(accountProfiles, profile)
		}

		fmt.Printf("\nCreating %d accounts using catchall\n", CREATE_COUNT)
	}

	var profileQueue = make(chan Profile)

	go func() {
		for {
			profile, ok := grabProfile()
			if !ok {
				close(profileQueue)
				break
			}
			profileQueue <- profile
		}
	}()

	var wg sync.WaitGroup

	for range numWorkers {
		wg.Add(1)
		go worker(&wg, profileQueue, config.Delay)
	}

	wg.Wait()

	CloseCSV()
}

func worker(wg *sync.WaitGroup, profileQueue chan Profile, delay int) {
	defer wg.Done()

	for profile := range profileQueue {
		err := InitializeSession(profile)

		if err != nil {
			if CATCHALL_DOMAIN != "" {
				profile := Profile{
					Email:             generateUsername(),
					ShippingFirstName: randomFirstName(),
					ShippingLastName:  randomLastName(),
				}
				accountProfiles = append(accountProfiles, profile)
			}

			if include_created {
				if strings.Contains(err.Error(), "email already used") {
					errRemove := removeUsedAccountFromTxt(profile.Email)
					if errRemove != nil {
						fmt.Printf("Warning: Failed to remove account from CSV: %v\n", err)
					}
				}
			}

			printRed(fmt.Sprintf("%v\n", err))
			continue
		}

		if CATCHALL_DOMAIN == "" {
			err = removeUsedAccountFromTxt(profile.Email)
			if err != nil {
				fmt.Printf("Warning: Failed to remove account from CSV: %v\n", err)
			}
		}

		time.Sleep(time.Duration(delay) * time.Second)
	}
}
