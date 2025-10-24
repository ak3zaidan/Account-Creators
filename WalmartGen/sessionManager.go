package main

import (
	"fmt"
	"sync"

	fhttp "github.com/bogdanfinn/fhttp"
	tls_client "github.com/bogdanfinn/tls-client"
)

type SessionData struct {
	Session tls_client.HttpClient
}

type CookieData struct {
	Domain string
	Cookie *fhttp.Cookie
}

var (
	freshSessionsMutex sync.Mutex
	freshSessions      []*SessionData
)

func InitializeSession(prof Profile) error {
	// freshSessionsMutex.Lock()
	// defer freshSessionsMutex.Unlock()

	err := setup(getNextProxy(), prof)
	if err != nil {
		return fmt.Errorf("%w", err)
	}

	return nil
}

func GetFreshSession() (*SessionData, error) {
	freshSessionsMutex.Lock()
	defer freshSessionsMutex.Unlock()

	if len(freshSessions) == 0 {
		return nil, fmt.Errorf("no fresh sessions available")
	}

	return freshSessions[0], nil
}

func GetFreshSessionCount() int {
	freshSessionsMutex.Lock()
	defer freshSessionsMutex.Unlock()
	return len(freshSessions)
}
