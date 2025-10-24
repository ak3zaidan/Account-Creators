package main

import (
	"bufio"
	"bytes"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"reflect"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
	"unicode"

	"github.com/bogdanfinn/fhttp/cookiejar"
	"github.com/bogdanfinn/tls-client/profiles"
	"github.com/fatih/color"

	"slices"

	fhttp "github.com/bogdanfinn/fhttp"
	tls_client "github.com/bogdanfinn/tls-client"
	"github.com/emersion/go-imap"
	"github.com/emersion/go-imap/client"
)

var EXTERNAL bool = true

// Get from API

var USE_OUTLOOK_API bool = false

// Creates batches of popmart accounts

var createBatches bool = false

var countryBatches []string = []string{
	"SG",
	"KR",
	"JP",
	"AU",
}

//
//
//
//

var Threads int = 55

var MainPASSWORD = "9VaultAccGOAT"

var PREMIUM_ACCOUNTS bool = false

// Command add go to path Conda: $env:PATH = "C:\Program Files\Go\bin;" + $env:PATH
// Request Based Gen (can run a lot)
// To run this:
// 1: cd PopmartGen
// 2: go run main.go

var HOST = "imap.gmail.com"
var IMAPUSERNAME = "@gmail.com"
var IMAPPASSWORD = ""

// If this is true the bot will use outlook emails from 'outlook.txt' and you can ignore IMAP stuff

var OUTLOOK_EMAILS bool = true

var SHUFFLE_OUTLOOKS bool = true

// If true, adds the outlooks to 'linkedOutlooks.txt' for accounts that succeed for users that want popmart email access. Only do this for trusted type

var SAVE_LINKED_MAILS bool = true
var NUMBER_TO_MAKE int = 500

//
//
//
//

var RANDOM_PASSWORD bool = false

var ADD_ADDRESS bool = false
var JIG_ADDRESS bool = false
var EXPORT_ADDRESS bool = false

var city string = ""
var address1 string = ""
var address2 string = ""
var state string = "IL"
var countryShip string = "US"
var phone string = "312876"
var lastName string = ""
var firstName string = ""
var postalCode string = "61265"

//
//
//
//
//
//

var Region string = "DE"

// United States -> "US"
// Canada -> "CA"
// Brazil -> "BR"
// Australia -> "AU"
// New Zealand -> "NZ"
// Austria -> "AT"
// Belgium -> "BE"
// Croatia -> "HR"
// Czech Republic -> "CZ"
// Denmark -> "DK"
// Estonia -> "EE"
// Finland -> "FI"
// France -> "FR"
// Germany -> "DE"
// Greece -> "GR"
// Hungary -> "HU"
// Ireland -> "IE"
// Italy -> "IT"
// Latvia -> "LV"
// Lithuania -> "LT"
// Luxembourg -> "LU"
// Netherlands -> "NL"
// Poland -> "PL"
// Portugal -> "PT"
// Slovakia -> "SK"
// Slovenia -> "SI"
// Spain -> "ES"
// Sweden -> "SE"
// Switzerland -> "CH"
// United Kingdom -> "GB"
// Hong Kong -> "HK"
// Indonesia -> "ID"
// Japan -> "JP"
// Macao -> "MO"
// Malaysia -> "MY"
// Philippines -> "PH"
// Singapore -> "SG"
// South Korea -> "KR"
// Taiwan -> "TW"
// Thailand -> "TH"
// Vietnam -> "VN"

//
//
//
//
//
//
//
//
//

// (Only for gmail) Between 1-3, putting it as 1 makes double the accounts as email, putting it as 3 triples

var DotMethodScaleFactor int = 0

// If this is true then the bot will use random emails and you can ignore IMAP stuff, will run forever with this mode

var RANDOM_TEMP_EMAILS bool = false

// Extra Params

var USE_CLIENT_POOL bool = false
var REQUIRE_IP bool = false
var USE_CHARLES bool = false
var USE_CLOUD_FUNC bool = false
var USE_CODE_INPUT bool = false
var RESI_TYPE = "resis.txt"
var USE_RESIS = true
var USE_PROXIES = true
var SAFE_MODE bool = false

// Ignore

var EP1 string = "/us/user/login"
var EP2 string = "/us/user/register"
var EP3 string = "/us/account/manage"
var EP4 string = "/us/account"

var UID string = "dq1abAfRnTTLVoTVxr1LK4gNfNb2"

var profile profiles.ClientProfile = profiles.Chrome_133

var currentChrome int = 138

var chromeVersions = map[int][]string{
	133: {
		"133.0.5678.45",
		"133.0.5678.92",
		"133.0.5678.120",
	},
	134: {
		"134.0.5732.10",
		"134.0.5732.65",
		"134.0.5732.88",
	},
	135: {
		"135.0.5801.15",
		"135.0.5801.70",
		"135.0.5801.99",
	},
	136: {
		"136.0.5860.20",
		"136.0.5860.75",
		"136.0.5860.114",
	},
	137: {
		"137.0.7151.55",
		"137.0.7151.56",
		"137.0.7151.119",
		"137.0.7151.120",
	},
	138: {
		"138.0.7204.96",
		"138.0.7204.97",
	},
}

var chromeSecChUaHeaders = map[int]string{
	133: `"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"`,
	134: `"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"`,
	135: `"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"`,
	136: `"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"`,
	137: `"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"`,
	138: `"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"`,
}

const LOCAL_EP = "http://127.0.0.1:8080"
const CLOUD_EP = "https://td-solver-.us-central1.run.app"

var domains []string = []string{}
var proxies []string = []string{}
var emails []string = []string{}
var emailsDup []string = []string{}
var dupLock sync.RWMutex
var generalLock sync.RWMutex
var imapClient *client.Client
var imapLock sync.RWMutex
var cachedCodeData map[string]string
var cacheLock sync.RWMutex
var isRetry bool = false

var realIpsLock sync.RWMutex
var realIps map[string]string
var publicIP string = ""

var namespace string = ""
var clientKey string = ""
var country string = ""
var projectId string = ""
var lang string = ""

var registerEp string
var loginEp string
var updateEp string
var shipEp string

var rng = rand.New(rand.NewSource(time.Now().UnixNano()))
var rngMu sync.Mutex
var randName = rand.New(rand.NewSource(time.Now().UnixNano()))
var rngMuName sync.Mutex
var randProfile = rand.New(rand.NewSource(time.Now().UnixNano()))
var rngMuProfile sync.Mutex

var createTotal int = 0
var createMu sync.RWMutex

var clientPool []ClientWithProxy
var clientMu sync.Mutex

func main() {
	if createBatches {
		for index, batchRegion := range countryBatches {
			Region = batchRegion
			MainPASSWORD = MainPASSWORD + strconv.Itoa(index)

			entry()

			time.Sleep(500 * time.Second)
		}
	} else {
		if len(os.Args) > 1 {
			arg := os.Args[1]

			Region = arg
		}

		entry()
	}
}

func entry() {
	realIps = make(map[string]string)
	cachedCodeData = make(map[string]string)
	data := GetPopmartCountryData(Region)

	namespace = data["namespace"]
	clientKey = data["clientKey"]
	country = data["country"]
	projectId = data["projectId"]
	lang = data["lang"]

	region := strings.ToLower(Region)
	loginEp = "https://www.popmart.com/" + region + "/user/login"
	registerEp = "https://www.popmart.com/" + region + "/user/register"
	updateEp = "https://www.popmart.com/" + region + "/account/manage"
	shipEp = "https://www.popmart.com/" + region + "/account"
	EP1 = "/" + region + "/user/login"
	EP2 = "/" + region + "/user/register"
	EP3 = "/" + region + "/account/manage"
	EP4 = "/" + region + "/account"

	if USE_OUTLOOK_API {
		for range 500000 {
			emails = append(emails, "")
		}
	} else if OUTLOOK_EMAILS {
		loadOutlooks()
	} else if RANDOM_TEMP_EMAILS {
		for range 10000 {
			emails = append(emails, "")
		}

		gotDomains, err := GetDomains()

		if err != nil {
			fmt.Printf("Error getting domains: %v", err)
			return
		} else {
			fmt.Printf("\nFetched %d domains to use", len(gotDomains))
		}

		domains = gotDomains
	} else {
		loadEmails()
	}

	loadProxies()

	if !OUTLOOK_EMAILS && !RANDOM_TEMP_EMAILS && !USE_OUTLOOK_API {
		log.Println("Connecting to IMAP server...")
		var err error

		// Connect to server using TLS
		imapClient, err = client.DialTLS(fmt.Sprintf("%s:993", HOST), nil)
		if err != nil {
			panic(err)
		}
		defer imapClient.Logout()

		// Login
		if err := imapClient.Login(IMAPUSERNAME, IMAPPASSWORD); err != nil {
			panic(err)
		}
		log.Println("Logged in successfully")

		// Select INBOX
		_, err = imapClient.Select("INBOX", false)
		if err != nil {
			panic(err)
		}
	}

	if USE_CLIENT_POOL {
		setupClientPool()
	}

	workerPool()

	if SAVE_LINKED_MAILS && OUTLOOK_EMAILS {
		if createTotal >= NUMBER_TO_MAKE {
			fmt.Println("\n\nDone.")
			return
		}
	}

	if !EXTERNAL {
		if clearAndRetry() {
			isRetry = true

			tempMap := make(map[string]string)
			cachedCodeData = tempMap

			workerPool()
		}
	}

	fmt.Println("\n\nDone.")
}

type ClientWithProxy struct {
	Client tls_client.HttpClient
	Proxy  string
}

func setupClientPool() {
	for _, proxy := range proxies {
		ip, port, username, password := parseProxy(proxy)
		client, err := getClient(ip, port, username, password)
		if err != nil {
			fmt.Printf("Failed to create client for proxy %s: %v\n", proxy, err)
			continue
		}
		clientPool = append(clientPool, ClientWithProxy{
			Client: client,
			Proxy:  proxy,
		})
	}
}

func workerPool() {
	work := make(chan int)
	var wg sync.WaitGroup

	for range Threads {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for index := range work {

				if SAVE_LINKED_MAILS && OUTLOOK_EMAILS {
					createMu.RLock()

					if createTotal >= NUMBER_TO_MAKE {
						fmt.Println("\n\n-> Worker stopping, reached limit")
						createMu.RUnlock()
						break
					} else {
						createMu.RUnlock()
					}
				}

				fmt.Printf("\nCreating account %d\n", index)
				generalLock.RLock()
				createEmail := emails[index]
				generalLock.RUnlock()

				createAccount(createEmail)

				if EXTERNAL {
					return
				}
			}
		}()
	}

	go func() {
		for i := range len(emails) {
			work <- i
		}

		close(work)
	}()

	wg.Wait()
}

func createAccount(email string) {
	UserAgent, SecChUa, ChromeFullVersion := randomChromeData()

	green := color.New(color.FgGreen).SprintFunc()
	blue := color.New(color.FgBlue).SprintFunc()
	purple := color.New(color.FgHiMagenta).SprintFunc()
	cyan := color.New(color.FgHiCyan).SprintFunc()
	red := color.New(color.FgRed).SprintFunc()

	if RANDOM_TEMP_EMAILS {
		email = GetRandomEmail()

		println("Using email: ", email)
	}

	var newPassword string = ""
	retryEmail := email

	var outlookRefresh string = ""
	var outlookClient string = ""
	var pollErr error = nil

	if USE_OUTLOOK_API {
		email, _, outlookRefresh, outlookClient, pollErr = pollForOutlookAccount()

		if pollErr != nil {
			println(red("\n-> API is OOS"))
			return
		}
	} else if OUTLOOK_EMAILS {
		if strings.Contains(email, "----") {
			parts := strings.SplitN(email, "----", 4)

			email = parts[0]
			outlookRefresh = parts[2]
			outlookClient = parts[3]
		} else {
			parts := strings.SplitN(email, ":", 4)

			email = parts[0]
			outlookRefresh = parts[2]
			outlookClient = parts[3]
		}
	} else if strings.Contains(email, ".com:") {
		parts := strings.SplitN(email, ":", 2)

		email = parts[0]
		newPassword = parts[1]
	}

	// Step 1
	var ip string = ""
	var port string = ""
	var username string = ""
	var proxyPass string = ""
	var singleProxy string = ""
	var clientError error = nil
	var client tls_client.HttpClient

	if USE_CLIENT_POOL {
		clientMu.Lock()

		if len(clientPool) == 0 {
			clientMu.Unlock()
			fmt.Println("No clients available")
			return
		}

		var clientEntry ClientWithProxy
		lastIndex := len(clientPool) - 1
		clientEntry = clientPool[lastIndex]
		clientPool = clientPool[:lastIndex]

		clientMu.Unlock()

		client = clientEntry.Client
		singleProxy = clientEntry.Proxy
	} else {
		if USE_PROXIES {
			ip, port, username, proxyPass = getRandomProxy()

			if ip != "" {
				singleProxy = fmt.Sprintf("%s:%s:%s:%s", ip, port, username, proxyPass)
			}
		}

		client, clientError = getClient(ip, port, username, proxyPass)
		if clientError != nil {
			fmt.Printf("\nError creating client: %v", clientError)
			return
		}
	}

	// Get IP
	var proxyIP string = ""

	if REQUIRE_IP {
		proxyIP = SetIP(client, singleProxy)

		if proxyIP == "" {
			fmt.Println("Error getting proxy IP")
			return
		}
	}

	// Step 2
	var data1 string = "/customer/v1/customer/exist"
	var data2 string = loginEp
	var data3 string = EP1

	if !SAFE_MODE {
		data1 = "/customer/v1/verification/send"
		data2 = registerEp
		data3 = EP2
	}

	session, sessionErr := Gen(singleProxy, data1, data2, proxyIP, data3, UserAgent, SecChUa, ChromeFullVersion)
	if sessionErr != nil || session.Token == "" {
		fmt.Printf("\nError getting session: %v", sessionErr)
		return
	}
	fmt.Printf("\nSession setup for email! %s", email)

	if SAFE_MODE {
		// Step 3
		existStatus := CheckUser(client, email, session.Sign, session.Key, UserAgent, SecChUa)
		if existStatus != "" {
			fmt.Printf("\n%v", existStatus)
			return
		}

		// Step 4
		newData1, recalErr1 := Recalculate(session.Token, "/customer/v1/verification/send", registerEp, session.WebGl, EP2, session.Fp, UserAgent)
		if recalErr1 != nil || newData1 == nil {
			fmt.Printf("\nError getting key and sign for register: %v", recalErr1)
			return
		}

		session.Key = newData1.Key
		session.Sign = newData1.Sign
	}

	// Step 5
	success := sendCode(client, email, session.Key, session.Sign, UserAgent, SecChUa)
	if success != nil {
		fmt.Printf("\nError sending code: %v", success)
		return
	}

	fmt.Printf("\nEmail waiting for code! %s", email)

	// Step 6
	var code string = ""
	var codeError error

	if OUTLOOK_EMAILS {
		code, codeError = getOutlookOTP(email, outlookRefresh, outlookClient)
	} else if RANDOM_TEMP_EMAILS {
		code, codeError = FetchPopmartOTP(email)
	} else {
		startTime := time.Now()
		if isRetry && findEmailIndex(email) < Threads {
			time.Sleep(25 * time.Second)
		} else {
			time.Sleep(10 * time.Second)
		}
		code, codeError = recursiveCodeChecker(email, startTime)
	}

	cacheLock.Lock()
	delete(cachedCodeData, email)
	cacheLock.Unlock()

	if codeError != nil {
		fmt.Printf("\nError getting code: %v", codeError)
		return
	}

	println(green("\nEmail found code! " + email + " -> " + code + "."))

	// Step 7
	newData2, recalErr2 := Recalculate(session.Token, "/customer/v1/customer/register", registerEp, session.WebGl, EP2, session.Fp, UserAgent)
	if recalErr2 != nil || newData2 == nil {
		fmt.Printf("\nError getting key and sign for register: %v", recalErr2)
		return
	}

	// Step 8
	if newPassword == "" {
		if RANDOM_PASSWORD {
			newPassword = Random3CharString() + randomDigits(3) + Random3CharString()
		} else {
			newPassword = MainPASSWORD
		}
	}
	token, identityId, nickname, gid, registerErr := register(client, email, newPassword, code, newData2.Key, newData2.Sign, UserAgent, SecChUa)
	if registerErr != nil {
		println(red(fmt.Sprintf("\nError registering: %v", registerErr)))
		return
	}

	if ADD_ADDRESS {
		time.Sleep(5 * time.Second)

		newData3, recalErr3 := Recalculate(session.Token, "/customer/v1/customer/update", shipEp, session.WebGl, EP4, session.Fp, UserAgent)
		if recalErr3 != nil || newData3 == nil {
			fmt.Printf("\nError getting key and sign for profile fill: %v", recalErr3)
			return
		}

		if nickname == "" {
			nickname = getNickname(email)
		}

		addressAdded, xName, xPhone, xAddress1, xAddress2, addyErr := AddAddress(client, UserAgent, SecChUa, nickname, token, newData3.Sign, newData3.Key)

		if addyErr != "" {
			println(red("\n-> Shipping add error: " + addyErr))
			return
		}
		if addressAdded == nil {
			println(red("\n-> Shipping failed add: " + email))
			return
		}

		if EXPORT_ADDRESS {
			addAccountAddress(email, newPassword, xName, xPhone, xAddress1, xAddress2)
		}

		println(cyan("\n-> Shipping address added!: " + email))
	}

	createMu.Lock()
	createTotal += 1
	createMu.Unlock()

	println(blue("\nAcc made!: " + email + " version " + ChromeFullVersion))
	addAccount(email, newPassword, retryEmail)

	if PREMIUM_ACCOUNTS {
		if token == "" || identityId == "" {
			println(red("\n-> Profile failed setup 1: " + email))
			return
		}

		time.Sleep(5 * time.Second)

		newData4, recalErr4 := Recalculate(session.Token, "/customer/v1/customer/update", updateEp, session.WebGl, EP3, session.Fp, UserAgent)
		if recalErr4 != nil || newData4 == nil {
			fmt.Printf("\nError getting key and sign for profile fill: %v", recalErr4)
			return
		}

		fillErr := FillProfile(client, email, token, identityId, newData4.Key, newData4.Sign, UserAgent, SecChUa, gid)

		if fillErr == nil {
			println(purple("\n-> Profile info setup!: " + email))
		} else {
			println(red("\n-> Profile failed setup 2: " + email))
		}
	}
}

func register(client tls_client.HttpClient, email, password, code, key, sign, UserAgent, SecChUa string) (string, string, string, int, error) {
	epochTime := time.Now().Unix()
	hashBase := fmt.Sprintf("{\"captcha_data\":null,\"code\":\"%s\",\"country\":\"%s\",\"email\":\"%s\",\"password\":\"%s\",\"subscribe_email\":1}W_ak^moHpMla%d",
		code,
		strings.ToLower(country),
		email,
		password,
		epochTime,
	)
	queryHash := ToMd5(hashBase)

	payload := fmt.Sprintf("{\"password\":\"%s\",\"code\":\"%s\",\"country\":\"%s\",\"subscribe_email\":%d,\"email\":\"%s\",\"captcha_data\":null,\"s\":\"%s\",\"t\":%d}",
		password,
		code,
		strings.ToLower(country),
		1,
		email,
		queryHash,
		epochTime,
	)

	req, err1 := fhttp.NewRequest(http.MethodPost, domainForRegion()+"/customer/v1/customer/register", bytes.NewBufferString(payload))
	if err1 != nil {
		return "", "", "", 0, err1
	}

	req.Header = fhttp.Header{
		"language":           {lang},
		"sec-ch-ua-platform": {`"Windows"`},
		"x-project-id":       {projectId},
		"x-device-os-type":   {"web"},
		"sec-ch-ua":          {SecChUa},
		"td-session-sign":    {sign},
		"sec-ch-ua-mobile":   {"?0"},
		"grey-secret":        {"null"},
		"accept":             {"application/json, text/plain, */*"},
		"content-type":       {"application/json"},
		"td-session-query":   {""},
		"x-client-country":   {country},
		"td-session-key":     {key},
		"tz":                 {"America/New_York"},
		"td-session-path":    {"/customer/v1/customer/register"},
		"country":            {country},
		"x-sign":             {xSignReq(clientKey, epochTime)},
		"clientkey":          {clientKey},
		"user-agent":         {UserAgent},
		"x-client-namespace": {namespace},
		"origin":             {"https://www.popmart.com"},
		"sec-fetch-site":     {"same-site"},
		"sec-fetch-mode":     {"cors"},
		"sec-fetch-dest":     {"empty"},
		"referer":            {"https://www.popmart.com/"},
		"accept-encoding":    {"gzip, deflate, br, zstd"},
		"accept-language":    {"en-US,en;q=0.9"},
		"priority":           {"u=1, i"},
		fhttp.HeaderOrderKey: {
			"content-length",
			"language",
			"sec-ch-ua-platform",
			"x-project-id",
			"x-device-os-type",
			"sec-ch-ua",
			"td-session-sign",
			"sec-ch-ua-mobile",
			"grey-secret",
			"accept",
			"content-type",
			"td-session-query",
			"x-client-country",
			"td-session-key",
			"tz",
			"td-session-path",
			"country",
			"x-sign",
			"clientkey",
			"user-agent",
			"x-client-namespace",
			"origin",
			"sec-fetch-site",
			"sec-fetch-mode",
			"sec-fetch-dest",
			"referer",
			"accept-encoding",
			"accept-language",
			"priority",
		},
	}

	resp, err2 := client.Do(req)
	if err2 != nil {
		return "", "", "", 0, err2
	}
	defer resp.Body.Close()

	body, err3 := io.ReadAll(resp.Body)
	if err3 != nil {
		return "", "", "", 0, err3
	}

	var result map[string]any
	err4 := json.Unmarshal(body, &result)
	if err4 != nil {
		return "", "", "", 0, err4
	}

	message, ok := result["message"].(string)
	if !ok {
		return "", "", "", 0, fmt.Errorf("no message in registration")
	}

	if Region == "MO" {
		if message != "成功" {
			return "", "", "", 0, fmt.Errorf("message is not success: %s", message)
		}
	} else if Region == "TH" {
		if message != "สำเร็จ" {
			return "", "", "", 0, fmt.Errorf("message is not success: %s", message)
		}
	} else if message != "success" {
		return "", "", "", 0, fmt.Errorf("message is not success: %s", message)
	}

	// Get user data

	var response SignResp
	if err := json.Unmarshal(body, &response); err == nil {
		if response.Code == "OK" {
			return response.Data.Token, response.Data.User.IdentityId, response.Data.User.Nickname, response.Data.User.Gid, nil
		}
	}

	return "", "", "", 0, nil
}

func recursiveCodeChecker(findEmail string, startTime time.Time) (string, error) {
	if USE_CODE_INPUT {
		reader := bufio.NewReader(os.Stdin)
		fmt.Print("\nEnter code: ")
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		return input, nil
	}

	content, checkError := getCode(findEmail)

	if checkError != nil {
		fmt.Printf("\nError getting emails retrying (%v)", checkError)
	}

	if content != "" {
		words := strings.Fields(content)

		for _, word := range words {
			if allDigits(word) {
				return word, nil
			}
		}
	}

	if isSixtySecondsOld(startTime) {
		return "", fmt.Errorf("expired: code not found")
	} else {
		time.Sleep(5 * time.Second)
		return recursiveCodeChecker(findEmail, startTime)
	}
}

func getCode(findEmail string) (string, error) {
	// First check under read lock
	cacheLock.RLock()
	storedData, found := cachedCodeData[findEmail]
	cacheLock.RUnlock()
	if found {
		return storedData, nil
	}

	// Wait for IMAP lock (may block)
	imapLock.Lock()
	defer imapLock.Unlock()

	// Recheck cache AFTER acquiring imapLock
	cacheLock.RLock()
	storedData, found = cachedCodeData[findEmail]
	cacheLock.RUnlock()
	if found {
		return storedData, nil
	}

	// Get mailbox status to determine message count
	mbox, err := imapClient.Status("INBOX", []imap.StatusItem{imap.StatusMessages})
	if err != nil {
		return "", err
	}

	// Calculate range for the newest x(Threads) messages
	from := uint32(1)
	to := mbox.Messages
	if to > uint32(Threads) {
		from = to - (uint32(Threads) - 1) // To get x(Threads) messages (from to inclusive)
	}

	// Create a new sequence set for fetching
	seqSet := new(imap.SeqSet)
	seqSet.AddRange(from, to)

	// Items to fetch
	fetchItems := []imap.FetchItem{
		imap.FetchAll,
	}

	// Create channel for messages
	messages := make(chan *imap.Message, Threads)
	done := make(chan error, 1)

	// Start fetching
	go func() {
		done <- imapClient.Fetch(seqSet, fetchItems, messages)
	}()

	// Process messages as they arrive
	lowerQuery := strings.ToLower(findEmail)

	var allMessages []*imap.Message
	for msg := range messages {
		allMessages = append(allMessages, msg)
	}

	for i := len(allMessages) - 1; i >= 0; i-- {

		msg := allMessages[i]

		if !IsWithinLast80Seconds(msg.InternalDate) {
			continue
		}

		if msg != nil && msg.Envelope != nil {

			var recipients []*imap.Address
			if msg.Envelope.To != nil {
				recipients = append(recipients, msg.Envelope.To...)
			}

			for _, recipient := range recipients {
				if recipient != nil {
					currentEmail := strings.ToLower(recipient.Address())

					if CheckEmail(currentEmail, lowerQuery) {
						// Found our target email, return the subject as code
						return msg.Envelope.Subject, nil
					} else {
						// Check if this email is for another task we're processing
						generalLock.RLock()
						emailsCopy := make([]string, len(emails))
						copy(emailsCopy, emails)
						generalLock.RUnlock()

						for _, otherTaskEmail := range emailsCopy {
							if CheckEmail(currentEmail, strings.ToLower(otherTaskEmail)) {
								cacheLock.Lock()
								cachedCodeData[otherTaskEmail] = msg.Envelope.Subject
								cacheLock.Unlock()
							}
						}
					}
				}
			}
		}
	}

	// Check for fetch errors
	if err := <-done; err != nil {
		return "", err
	}

	return "", nil
}

func sendCode(client tls_client.HttpClient, email, key, sign, UserAgent, SecChUa string) error {
	epochTime := time.Now().Unix()
	hashBase := fmt.Sprintf("{\"module\":\"register\",\"providerId\":\"%s\",\"providerType\":\"email\"}W_ak^moHpMla%d",
		email,
		epochTime,
	)
	queryHash := ToMd5(hashBase)

	payload := fmt.Sprintf("{\"providerId\":\"%s\",\"providerType\":\"email\",\"module\":\"register\",\"s\":\"%s\",\"t\":%d}",
		email,
		queryHash,
		epochTime,
	)

	req, err1 := fhttp.NewRequest(http.MethodPost, domainForRegion()+"/customer/v1/verification/send", bytes.NewBufferString(payload))
	if err1 != nil {
		return err1
	}

	req.Header = fhttp.Header{
		"language":           {lang},
		"sec-ch-ua-platform": {`"Windows"`},
		"x-project-id":       {projectId},
		"x-device-os-type":   {"web"},
		"sec-ch-ua":          {SecChUa},
		"td-session-sign":    {sign},
		"sec-ch-ua-mobile":   {"?0"},
		"grey-secret":        {"null"},
		"accept":             {"application/json, text/plain, */*"},
		"content-type":       {"application/json"},
		"td-session-query":   {""},
		"x-client-country":   {country},
		"td-session-key":     {key},
		"tz":                 {"America/New_York"},
		"td-session-path":    {"/customer/v1/verification/send"},
		"country":            {country},
		"x-sign":             {xSignReq(clientKey, epochTime)},
		"clientkey":          {clientKey},
		"user-agent":         {UserAgent},
		"x-client-namespace": {namespace},
		"origin":             {"https://www.popmart.com"},
		"sec-fetch-site":     {"same-site"},
		"sec-fetch-mode":     {"cors"},
		"sec-fetch-dest":     {"empty"},
		"referer":            {"https://www.popmart.com/"},
		"accept-encoding":    {"gzip, deflate, br, zstd"},
		"accept-language":    {"en-US,en;q=0.9"},
		"priority":           {"u=1, i"},
		fhttp.HeaderOrderKey: {
			"content-length",
			"language",
			"sec-ch-ua-platform",
			"x-project-id",
			"x-device-os-type",
			"sec-ch-ua",
			"td-session-sign",
			"sec-ch-ua-mobile",
			"grey-secret",
			"accept",
			"content-type",
			"td-session-query",
			"x-client-country",
			"td-session-key",
			"tz",
			"td-session-path",
			"country",
			"x-sign",
			"clientkey",
			"user-agent",
			"x-client-namespace",
			"origin",
			"sec-fetch-site",
			"sec-fetch-mode",
			"sec-fetch-dest",
			"referer",
			"accept-encoding",
			"accept-language",
			"priority",
		},
	}

	resp, err2 := client.Do(req)
	if err2 != nil {
		return err2
	}
	defer resp.Body.Close()

	body, err3 := io.ReadAll(resp.Body)
	if err3 != nil {
		return err3
	}

	client.CloseIdleConnections()

	var result map[string]any
	err4 := json.Unmarshal(body, &result)
	if err4 != nil {
		return err4
	}

	message, ok := result["message"].(string)
	if !ok {
		return fmt.Errorf("no message in verification")
	}

	if Region == "MO" {
		if message != "成功" {
			return fmt.Errorf("message is not success: %s", message)
		}
	} else if Region == "TH" {
		if message != "สำเร็จ" {
			return fmt.Errorf("message is not success: %s", message)
		}
	} else if message != "success" {
		return fmt.Errorf("message is not success: %s", message)
	}

	return nil
}

func CheckUser(client tls_client.HttpClient, email, TdSign, TdKey, UserAgent, SecChUa string) string {
	endPoint := domainForRegion() + "/customer/v1/customer/exist"

	epochTime := time.Now().Unix()
	hashBase := fmt.Sprintf("{\"email\":\"%s\"}W_ak^moHpMla%d",
		email,
		epochTime,
	)
	queryHash := ToMd5(hashBase)

	payload := fmt.Sprintf(`{"email":"%s","s":"%s","t":%d}`,
		email,
		queryHash,
		epochTime,
	)

	req, err := fhttp.NewRequest(fhttp.MethodPost, endPoint, bytes.NewBufferString(payload))
	if err != nil {
		return fmt.Sprintf("Check: Failed to create req: %v", err)
	}

	req.Header = fhttp.Header{
		"language":           {lang},
		"sec-ch-ua-platform": {"\"Windows\""},
		"x-project-id":       {projectId},
		"x-device-os-type":   {"web"},
		"sec-ch-ua":          {SecChUa},
		"td-session-sign":    {TdSign},
		"sec-ch-ua-mobile":   {"?0"},
		"grey-secret":        {"null"},
		"accept":             {"application/json, text/plain, */*"},
		"content-type":       {"application/json"},
		"td-session-query":   {""},
		"x-client-country":   {country},
		"td-session-key":     {TdKey},
		"tz":                 {"America/New_York"},
		"td-session-path":    {"/customer/v1/customer/exist"},
		"country":            {country},
		"x-sign":             {xSignReq(clientKey, epochTime)},
		"clientkey":          {clientKey},
		"user-agent":         {UserAgent},
		"x-client-namespace": {namespace},
		"origin":             {"https://www.popmart.com"},
		"sec-fetch-site":     {"same-site"},
		"sec-fetch-mode":     {"cors"},
		"sec-fetch-dest":     {"empty"},
		"referer":            {"https://www.popmart.com/"},
		"accept-encoding":    {"gzip, deflate, br, zstd"},
		"accept-language":    {"en-US,en;q=0.9"},
		"priority":           {"u=1, i"},
		fhttp.HeaderOrderKey: []string{
			"content-length",
			"language",
			"sec-ch-ua-platform",
			"x-project-id",
			"x-device-os-type",
			"sec-ch-ua",
			"td-session-sign",
			"sec-ch-ua-mobile",
			"grey-secret",
			"accept",
			"content-type",
			"td-session-query",
			"x-client-country",
			"td-session-key",
			"tz",
			"td-session-path",
			"country",
			"x-sign",
			"clientkey",
			"user-agent",
			"x-client-namespace",
			"origin",
			"sec-fetch-site",
			"sec-fetch-mode",
			"sec-fetch-dest",
			"referer",
			"accept-encoding",
			"accept-language",
			"priority",
		},
	}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Sprintf("Check: Failed to do req: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Sprintf("Check: Failed to read resp: %v", err)
	}

	var result map[string]any
	if err := json.Unmarshal(body, &result); err != nil {
		return fmt.Sprintf("Check: Failed to parse resp: %v", err)
	}

	if message, ok := result["message"].(string); ok {
		if Region == "MO" {
			if message == "帳號不存在" {
				return ""
			} else if message == "成功" {
				return "User already exists"
			} else {
				return "Check: " + message
			}
		} else if Region == "TH" {
			if message == "ไม่มีบัญชีนี้อยู่" {
				return ""
			} else if message == "สำเร็จ" {
				return "User already exists"
			} else {
				return "Check: " + message
			}
		} else {
			if message == "account does not exist" {
				return ""
			} else if message == "success" {
				return "User already exists"
			} else {
				return "Check: " + message
			}
		}
	}

	return "Check: Unknown error"
}

func FillProfile(client tls_client.HttpClient, email, auth, identityId, key, sign, UserAgent, SecChUa string, gid int) error {
	birthday := RandomDate()
	nickname := generateRandomUsername()
	phone := RandomUSPhoneNumber()
	epochTime := time.Now().Unix()

	hashData := map[string]any{
		"gid":        gid,
		"nickname":   nickname,
		"avatar":     "https://cdn-global.popmart.com/images/default-avatar.png",
		"birthday":   birthday,
		"gender":     1,
		"phone":      phone,
		"email":      email,
		"identityId": identityId,
	}

	queryHash := W(hashData, epochTime, "post")

	payload := fmt.Sprintf("{\"gid\":%d,\"nickname\":\"%s\",\"avatar\":\"https://cdn-global.popmart.com/images/default-avatar.png\",\"birthday\":\"%s\",\"gender\":1,\"phone\":\"%s\",\"email\":\"%s\",\"identityId\":\"%s\",\"s\":\"%s\",\"t\":%d}",
		gid,
		nickname,
		birthday,
		phone,
		email,
		identityId,
		queryHash,
		epochTime,
	)

	req, err1 := fhttp.NewRequest(http.MethodPost, domainForRegion()+"/customer/v1/customer/update", bytes.NewBufferString(payload))
	if err1 != nil {
		return err1
	}

	req.Header = fhttp.Header{
		"language":           {lang},
		"sec-ch-ua-platform": {`"Windows"`},
		"authorization":      {"Bearer " + auth},
		"x-project-id":       {projectId},
		"x-device-os-type":   {"web"},
		"sec-ch-ua":          {SecChUa},
		"td-session-sign":    {sign},
		"sec-ch-ua-mobile":   {"?0"},
		"grey-secret":        {"null"},
		"accept":             {"application/json, text/plain, */*"},
		"content-type":       {"application/json"},
		"td-session-query":   {""},
		"x-client-country":   {country},
		"td-session-key":     {key},
		"tz":                 {"America/New_York"},
		"td-session-path":    {"/customer/v1/customer/update"},
		"country":            {country},
		"x-sign":             {xSignReq(clientKey, epochTime)},
		"clientkey":          {clientKey},
		"user-agent":         {UserAgent},
		"x-client-namespace": {namespace},
		"origin":             {"https://www.popmart.com"},
		"sec-fetch-site":     {"same-site"},
		"sec-fetch-mode":     {"cors"},
		"sec-fetch-dest":     {"empty"},
		"referer":            {"https://www.popmart.com/"},
		"accept-encoding":    {"gzip, deflate, br, zstd"},
		"accept-language":    {"en-US,en;q=0.9"},
		"priority":           {"u=1, i"},
		fhttp.HeaderOrderKey: {
			"content-length",
			"language",
			"sec-ch-ua-platform",
			"authorization",
			"x-project-id",
			"x-device-os-type",
			"sec-ch-ua",
			"td-session-sign",
			"sec-ch-ua-mobile",
			"grey-secret",
			"accept",
			"content-type",
			"td-session-query",
			"x-client-country",
			"td-session-key",
			"tz",
			"td-session-path",
			"country",
			"x-sign",
			"clientkey",
			"user-agent",
			"x-client-namespace",
			"origin",
			"sec-fetch-site",
			"sec-fetch-mode",
			"sec-fetch-dest",
			"referer",
			"accept-encoding",
			"accept-language",
			"priority",
		},
	}

	resp, err2 := client.Do(req)
	if err2 != nil {
		return err2
	}
	defer resp.Body.Close()

	body, err3 := io.ReadAll(resp.Body)
	if err3 != nil {
		return err3
	}

	var result map[string]any
	err4 := json.Unmarshal(body, &result)
	if err4 != nil {
		return err4
	}

	message, ok := result["message"].(string)
	if !ok {
		return fmt.Errorf("no message in registration")
	}

	if Region == "MO" {
		if message != "成功" {
			return fmt.Errorf("message is not success: %s", message)
		}
	} else if Region == "TH" {
		if message != "สำเร็จ" {
			return fmt.Errorf("message is not success: %s", message)
		}
	} else if message != "success" {
		return fmt.Errorf("message is not success: %s", message)
	}

	return nil
}

type AddressSingle struct {
	Code string `json:"code"`
	Data struct {
		Address Address `json:"address"`
	} `json:"data"`
	Message string `json:"message"`
	Now     int64  `json:"now"`
	Ret     int    `json:"ret"`
}

type AddressRes struct {
	Code string `json:"code"`
	Data struct {
		Count int       `json:"count"`
		List  []Address `json:"list"`
	} `json:"data"`
	Message string `json:"message"`
	Now     int64  `json:"now"`
	Ret     int    `json:"ret"`
}

type Address struct {
	ID           int    `json:"id"`
	ProvinceName string `json:"provinceName"`
	CityName     string `json:"cityName"`
	CountryName  string `json:"countryName"`
	DetailInfo   string `json:"detailInfo"`
	ExtraAddress string `json:"extraAddress"`
	FamilyName   string `json:"familyName"`
	GivenName    string `json:"givenName"`
	MiddleName   string `json:"middleName"`
	TelNumber    string `json:"telNumber"`
	UserName     string `json:"userName"`
	PostalCode   string `json:"postalCode"`
	NationalCode string `json:"nationalCode"`
	Note         string `json:"note"`
	IsDefault    bool   `json:"isDefault"`
	Extra        string `json:"extra"`
	UserID       int    `json:"userID"`
	IdentityNum  string `json:"identityNum"`
	ProvinceCode string `json:"provinceCode"`
	TaxCode      string `json:"taxCode"`
}

func AddAddress(client tls_client.HttpClient, UserAgent, SecChUa, nickname, jwt, TdSign, TdKey string) (*Address, string, string, string, string, string) {
	info := GetStateInfo(state)

	var address1Local string = address1
	var address2Local string = address2
	var phoneLocal string = phone
	var firstLocal string = firstName
	var lastLocal string = lastName

	if JIG_ADDRESS {
		if address2Local == "" {
			address2Local = generateRandomAddress2()
		} else {
			address2Local += RandomCharString()
		}
	}
	if len(phoneLocal) == 6 {
		phoneLocal = phoneLocal + randomDigits(4)
	}
	if firstLocal == "" {
		firstLocal = randomFirstName()
	}
	if lastLocal == "" {
		lastLocal = randomLastName()
	}

	epochTime := time.Now().Unix()
	epochString := strconv.FormatInt(epochTime, 10)
	hashBase := `{"address":{"cityName":"` + city + `","countryName":"` + FullCountryName(countryShip) + `","detailInfo":"` + address1Local + `","extraAddress":"` + address2Local + `","familyName":"` + lastLocal + `","givenName":"` + firstLocal + `","nationalCode":"` + countryShip + `","postalCode":"` + postalCode + `","provinceCode":"` + info.ProvinceCode + `","provinceName":"` + info.ProvinceName + `","telNumber":"` + phoneLocal + `","userName":"` + nickname + `"}}W_ak^moHpMla` + epochString
	queryHash := ToMd5(hashBase)

	payload := `{"address":{"givenName":"` + firstLocal + `","familyName":"` + lastLocal + `","telNumber":"` + phoneLocal + `","detailInfo":"` + address1Local + `","extraAddress":"` + address2Local + `","cityName":"` + city + `","postalCode":"` + postalCode + `","nationalCode":"` + countryShip + `","userName":"` + nickname + `","countryName":"` + FullCountryName(countryShip) + `","provinceName":"` + info.ProvinceName + `","provinceCode":"` + info.ProvinceCode + `"},"s":"` + queryHash + `","t":` + epochString + `}`

	endPoint := domainForRegion() + "/customer/v1/address/add"

	req, err := fhttp.NewRequest(fhttp.MethodPost, endPoint, bytes.NewBufferString(payload))
	if err != nil {
		return nil, "", "", "", "", fmt.Sprintf("Add Address: err creating request: %v", err)
	}

	req.Header = fhttp.Header{
		"language":           {lang},
		"sec-ch-ua-platform": {`"Windows"`},
		"authorization":      {"Bearer " + jwt},
		"x-project-id":       {projectId},
		"x-device-os-type":   {"web"},
		"sec-ch-ua":          {SecChUa},
		"td-session-sign":    {TdSign},
		"sec-ch-ua-mobile":   {"?0"},
		"grey-secret":        {"null"},
		"accept":             {"application/json, text/plain, */*"},
		"content-type":       {"application/json"},
		"td-session-query":   {""},
		"x-client-country":   {country},
		"td-session-key":     {TdKey},
		"tz":                 {"America/New_York"},
		"td-session-path":    {"/customer/v1/customer/update"},
		"country":            {country},
		"x-sign":             {xSignReq(clientKey, epochTime)},
		"clientkey":          {clientKey},
		"user-agent":         {UserAgent},
		"x-client-namespace": {namespace},
		"origin":             {"https://www.popmart.com"},
		"sec-fetch-site":     {"same-site"},
		"sec-fetch-mode":     {"cors"},
		"sec-fetch-dest":     {"empty"},
		"referer":            {"https://www.popmart.com/"},
		"accept-encoding":    {"gzip, deflate, br, zstd"},
		"accept-language":    {"en-US,en;q=0.9"},
		"priority":           {"u=1, i"},
		fhttp.HeaderOrderKey: {
			"content-length",
			"language",
			"sec-ch-ua-platform",
			"authorization",
			"x-project-id",
			"x-device-os-type",
			"sec-ch-ua",
			"td-session-sign",
			"sec-ch-ua-mobile",
			"grey-secret",
			"accept",
			"content-type",
			"td-session-query",
			"x-client-country",
			"td-session-key",
			"tz",
			"td-session-path",
			"country",
			"x-sign",
			"clientkey",
			"user-agent",
			"x-client-namespace",
			"origin",
			"sec-fetch-site",
			"sec-fetch-mode",
			"sec-fetch-dest",
			"referer",
			"accept-encoding",
			"accept-language",
			"priority",
		},
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, "", "", "", "", fmt.Sprintf("Add Address: error on request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, "", "", "", "", fmt.Sprintf("Add Address: error on decode: %v", err)
	}

	var response AddressSingle
	if err := json.Unmarshal(body, &response); err == nil {
		if response.Code == "OK" {
			return &response.Data.Address, (firstLocal + " " + lastLocal), phoneLocal, address1Local, address2Local, ""
		} else if strings.Contains(string(body), "25011") {
			return nil, "", "", "", "", "Add Address Blocked"
		} else {
			return nil, "", "", "", "", "Add Address Err: " + response.Code + " " + response.Code
		}
	}

	var result map[string]any
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, "", "", "", "", fmt.Sprintf("Add Address: error on parse: %v", err)
	}

	message, ok := result["message"].(string)
	if !ok {
		return nil, "", "", "", "", "Add Address: unknown error"
	}

	return nil, "", "", "", "", fmt.Sprintf("Add Address: %s", message)
}

// Solver Endpoints

func Recalculate(tokenID, path, endpoint, webGL, endpointNoQuery, fingerprint, UserAgent string) (*RecalculateResponse, error) {
	var url string = LOCAL_EP + "/recalculate"

	if USE_CLOUD_FUNC {
		url = CLOUD_EP + "/recalculate"
	}

	payload := map[string]string{
		"tokenId":         tokenID,
		"ua":              UserAgent,
		"path":            path,
		"endpoint":        endpoint,
		"webGl":           webGL,
		"region":          Region,
		"endpointNoQuery": endpointNoQuery,
		"fingerprint":     fingerprint,
		"uid":             UID,
	}

	body, _ := json.Marshal(payload)

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		if body, err := io.ReadAll(resp.Body); err == nil {
			fmt.Println(string(body))
		}

		return nil, fmt.Errorf("%s", "recal failure, resp code : "+strconv.Itoa(resp.StatusCode))
	}

	var result RecalculateResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func Gen(proxy, path, endpoint, ip, endpointNoQuery, UserAgent, SecChUa, ChromeFullVersion string) (*GenResponse, error) {
	var url string = LOCAL_EP + "/gen"

	if USE_CLOUD_FUNC {
		url = CLOUD_EP + "/gen"
	}

	payload := map[string]string{
		"proxy":             proxy,
		"path":              path,
		"endpoint":          endpoint,
		"ua":                UserAgent,
		"secChUa":           SecChUa,
		"chromeFullVersion": ChromeFullVersion,
		"region":            Region,
		"ip":                ip,
		"endpointNoQuery":   endpointNoQuery,
		"uid":               UID,
	}

	body, _ := json.Marshal(payload)

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		if body, err := io.ReadAll(resp.Body); err == nil {
			fmt.Println(string(body))
		}

		return nil, fmt.Errorf("%s", "gen failure, resp code : "+strconv.Itoa(resp.StatusCode))
	}

	var result GenResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

// Structs

type RecalculateResponse struct {
	Sign string `json:"sign"`
	Key  string `json:"key"`
}

type GenResponse struct {
	Sign  string `json:"sign"`
	Key   string `json:"key"`
	Token string `json:"token"`
	WebGl string `json:"webGl"`
	Did   string `json:"did"`
	Fp    string `json:"fp"`
}

// User Structs

type SignResp struct {
	Code    string   `json:"code"`
	Data    SignData `json:"data"`
	Message string   `json:"message"`
	Now     int64    `json:"now"`
	Ret     int      `json:"ret"`
}

type SignData struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

type User struct {
	Gid        int    `json:"gid"`
	Nickname   string `json:"nickname"`
	Email      string `json:"email"`
	Country    string `json:"country"`
	Language   string `json:"language"`
	IsVerified bool   `json:"IsVerified"`
	IdentityId string `json:"identityId"`
	AuthType   string `json:"authType"`
	Account    string `json:"account"`
}

// Temp Outlooks

func getOutlookOTP(email, refresh, client string) (string, error) {
	pythonScript := "otp_script.py"

	cmd := exec.Command("python", pythonScript, email, refresh, client)

	var outBuf, errBuf bytes.Buffer
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf

	err := cmd.Run()

	if err != nil {
		return "", fmt.Errorf("script error: %v\nstderr: %s", err, errBuf.String())
	}

	output := outBuf.String()

	output = strings.TrimSpace(output)

	if output == "" {
		return "", fmt.Errorf("no OTP returned. stderr: %s", errBuf.String())
	}

	if !isSixDigits(output) {
		return "", fmt.Errorf("no OTP returned, output: %s", output)
	}

	return output, nil
}

// API

const (
	clientAPIKey = "1974c268e2494b9ebd2cb67fe12e9ceb488039"
	apiEndpoint  = "https://gapi.hotmail007.com/api/mail/getMail"
)

type MailResponse struct {
	Code    int      `json:"code"`
	Data    []string `json:"data"`
	Success bool     `json:"success"`
}

func pollForOutlookAccount() (email, password, refreshToken, clientID string, err error) {
	maxRetries := 500
	interval := 5 * time.Second

	mailType := "outlook"

	for i := range maxRetries {
		if mailType == "outlook" {
			mailType = "hotmail"
		} else {
			mailType = "outlook"
		}

		url := fmt.Sprintf("%s?clientKey=%s&mailType=%s&quantity=1", apiEndpoint, clientAPIKey, mailType)

		resp, err := http.Get(url)
		if err != nil {
			return "", "", "", "", fmt.Errorf("failed to make request: %w", err)
		}
		defer resp.Body.Close()

		body, _ := io.ReadAll(resp.Body)

		var mailResp MailResponse
		if err := json.Unmarshal(body, &mailResp); err != nil {
			return "", "", "", "", fmt.Errorf("failed to parse response: %w", err)
		}

		if mailResp.Success && len(mailResp.Data) > 0 {
			parts := strings.Split(mailResp.Data[0], ":")
			if len(parts) == 4 {
				return parts[0], parts[1], parts[2], parts[3], nil
			}
			return "", "", "", "", fmt.Errorf("unexpected data format: %s", mailResp.Data[0])
		}

		fmt.Printf("Retrying... (%d/%d)\n", i+1, maxRetries)
		time.Sleep(interval)
	}

	return "", "", "", "", fmt.Errorf("no account received after %d attempts", maxRetries)
}

// Random Catchall

type Message struct {
	ID      string `json:"id"`
	Subject string `json:"subject"`
	Text    string `json:"text"`
	HTML    string `json:"html"`
}

func GetRandomEmail() string {
	rngMu.Lock()
	defer rngMu.Unlock()

	if len(domains) == 0 {
		return ""
	}

	firstName := randomFirstName()
	lastName := randomLastName()

	username := generateRealisticUsername(rng, firstName, lastName)
	domain := domains[rng.Intn(len(domains))]

	return fmt.Sprintf("%s@%s", username, domain)
}

func generateRealisticUsername(rng *rand.Rand, firstName, lastName string) string {
	const digits = "0123456789"

	// Lowercase and sanitize names (optional)
	first := strings.ToLower(firstName)
	last := strings.ToLower(lastName)

	// Randomly choose a separator or no separator
	separators := []string{"", ".", "_", "-"}
	sep := separators[rng.Intn(len(separators))]

	username := first + sep + last

	// 50% chance to add a numeric suffix
	if rng.Intn(2) == 0 {
		username += randomString(rng, digits, rng.Intn(3)+1)
	}

	return username
}

func randomString(rng *rand.Rand, charset string, length int) string {
	var sb strings.Builder
	for range length {
		sb.WriteByte(charset[rng.Intn(len(charset))])
	}
	return sb.String()
}

func GetDomains() ([]string, error) {
	resp, err := http.Get("https://www.cybertemp.xyz/api/getDomains")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("failed to get domain: %s, status: %d", string(body), resp.StatusCode)
	}

	var domains []string
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	err = json.Unmarshal(body, &domains)
	if err != nil {
		return nil, err
	}

	return domains, nil
}

func FetchPopmartOTP(email string) (string, error) {
	const maxRetries = 10

	for attempt := range maxRetries {
		resp, err := http.Get("https://www.cybertemp.xyz/api/getMail?email=" + email)
		if err != nil {
			time.Sleep(time.Duration(2*(attempt+1)) * time.Second)
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode != 200 {
			fmt.Printf("Status code: %d", resp.StatusCode)
			time.Sleep(time.Second)
			continue
		}

		var messages []Message
		body, _ := io.ReadAll(resp.Body)
		json.Unmarshal(body, &messages)

		for _, msg := range messages {
			code := extractOTP(msg.Subject)
			if code != "" {
				return code, nil
			}
			code = extractOTP(msg.Text)
			if code != "" {
				return code, nil
			}
			code = extractOTP(msg.HTML)
			if code != "" {
				return code, nil
			}
		}
		time.Sleep(3500 * time.Millisecond)
	}
	return "", errors.New("verification code not found")
}

func extractOTP(content string) string {
	words := strings.Fields(content)
	for _, word := range words {
		if len(word) == 6 && allDigits(word) {
			return word
		}
	}
	return ""
}

// Helpers

func W(e any, t int64, n string) string {
	epochTimeString := strconv.FormatInt(t, 10)

	// Normalize function - equivalent to the inner function in JS
	var normalize func(any) any
	normalize = func(input any) any {
		if input == nil {
			return input
		}

		v := reflect.ValueOf(input)
		switch v.Kind() {
		case reflect.Slice, reflect.Array:
			// Handle arrays/slices
			result := make([]any, v.Len())
			for i := range v.Len() {
				result[i] = normalize(v.Index(i).Interface())
			}
			return result

		case reflect.Map:
			// Handle objects/maps
			if v.Type().Key().Kind() != reflect.String {
				return input
			}

			// Get all keys and sort them
			keys := make([]string, 0, v.Len())
			for _, key := range v.MapKeys() {
				keys = append(keys, key.String())
			}
			sort.Strings(keys)

			// Create new map with sorted keys
			result := make(map[string]any)
			for _, key := range keys {
				val := v.MapIndex(reflect.ValueOf(key))
				if val.IsValid() {
					result[key] = normalize(val.Interface())
				}
			}
			return result

		default:
			return input
		}
	}

	// Normalize the input
	o := normalize(e)

	// Convert to map for processing
	var objMap map[string]any
	if o != nil {
		if m, ok := o.(map[string]any); ok {
			objMap = m
		} else {
			// If it's not a map, create a temporary map to get JSON representation
			objMap = make(map[string]any)
		}
	} else {
		objMap = make(map[string]any)
	}

	// Get sorted keys
	keys := make([]string, 0, len(objMap))
	for k := range objMap {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	// Build the result map based on the mode
	a := make(map[string]any)
	for _, key := range keys {
		val := objMap[key]

		if n == "get" {
			// Only include non-empty, non-null values
			if val != nil && val != "" {
				a[key] = fmt.Sprintf("%v", val)
			}
		} else {
			a[key] = val
		}
	}

	// Convert to JSON string
	jsonBytes, err := json.Marshal(a)
	if err != nil {
		jsonBytes = []byte("{}")
	}
	jsonStr := string(jsonBytes)

	// Create the final string to hash
	finalStr := jsonStr + "W_ak^moHpMla" + epochTimeString

	// Create MD5 hash
	hash := md5.Sum([]byte(finalStr))
	return fmt.Sprintf("%x", hash)
}

func xSignReq(clientKey string, epochTime int64) string {
	stringToSign := fmt.Sprintf("%d,%s", epochTime, clientKey)
	return fmt.Sprintf("%s,%d", ToMd5(stringToSign), epochTime)
}

func ToMd5(text string) string {
	hash := md5.Sum([]byte(text))
	return hex.EncodeToString(hash[:])
}

func RandomDate() string {
	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	startDate := time.Date(2000, 1, 1, 0, 0, 0, 0, time.UTC)
	endDate := time.Date(2010, 12, 31, 23, 59, 59, 0, time.UTC)

	duration := endDate.Sub(startDate)

	randomDuration := time.Duration(randProfile.Int63n(int64(duration)))

	randomDate := startDate.Add(randomDuration)

	return randomDate.Format("2006-01-02")
}

func RandomUSPhoneNumber() string {
	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	areaCodes := []string{
		"201", "202", "203", "205", "206", "207", "208", "209", "210",
		"212", "213", "214", "215", "216", "217", "218", "219", "224",
		"225", "228", "229", "231", "234", "239", "240", "248", "251",
		"252", "253", "254", "256", "260", "262", "267", "269", "270",
		"276", "281", "301", "302", "303", "304", "305", "307", "308",
		"309", "310", "312", "313", "314", "315", "316", "317", "318",
		"319", "320", "321", "323", "325", "330", "334", "336", "337",
		"339", "347", "351", "352", "360", "361", "386", "401", "402",
		"404", "405", "406", "407", "408", "409", "410", "412", "413",
		"414", "415", "417", "419", "423", "424", "425", "430", "432",
		"434", "435", "440", "443", "464", "469", "470", "475", "478",
		"479", "480", "484", "501", "502", "503", "504", "505", "507",
		"508", "509", "510", "512", "513", "515", "516", "517", "518",
		"520", "530", "540", "541", "551", "559", "561", "562", "563",
		"564", "567", "570", "571", "573", "574", "575", "580", "585",
		"586", "601", "602", "603", "605", "606", "607", "608", "609",
		"610", "612", "614", "615", "616", "617", "618", "619", "620",
		"623", "626", "630", "631", "636", "641", "646", "650", "651",
		"660", "661", "662", "667", "678", "682", "701", "702", "703",
		"704", "706", "707", "708", "712", "713", "714", "715", "716",
		"717", "718", "719", "720", "724", "727", "731", "732", "734",
		"737", "740", "757", "760", "763", "765", "770", "772", "773",
		"774", "775", "781", "785", "786", "801", "802", "803", "804",
		"805", "806", "808", "810", "812", "813", "814", "815", "816",
		"817", "818", "828", "830", "831", "832", "843", "845", "847",
		"848", "850", "856", "857", "858", "859", "860", "862", "863",
		"864", "865", "870", "872", "878", "901", "903", "904", "906",
		"907", "908", "909", "910", "912", "913", "914", "915", "916",
		"917", "918", "919", "920", "925", "928", "929", "931", "936",
		"937", "940", "941", "947", "949", "951", "952", "954", "956",
		"970", "971", "972", "973", "978", "979", "980", "984", "985",
		"989",
	}

	areaCode := areaCodes[randProfile.Intn(len(areaCodes))]

	exchangeFirst := randProfile.Intn(8) + 2 // 2-9
	exchangeSecond := randProfile.Intn(10)   // 0-9
	exchangeThird := randProfile.Intn(10)    // 0-9

	subscriber := randProfile.Intn(10000)

	return fmt.Sprintf("%s%d%d%d%04d", areaCode, exchangeFirst, exchangeSecond, exchangeThird, subscriber)
}

func randomChromeData() (string, string, string) {
	rngMu.Lock()
	defer rngMu.Unlock()

	version := currentChrome // rng.Intn(currentChrome-133+1) + 133

	ua := "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + strconv.Itoa(version) + ".0.0.0 Safari/537.36"

	fullVersions := chromeVersions[version]
	fullVersion := fullVersions[rng.Intn(len(fullVersions))]

	secChUa := chromeSecChUaHeaders[version]

	return ua, secChUa, fullVersion
}

func IsWithinLast80Seconds(t time.Time) bool {
	duration := time.Since(t)
	return duration >= 0 && duration <= 80*time.Second
}

func getClient(ip, port, username, proxyPass string) (tls_client.HttpClient, error) {
	jar, _ := cookiejar.New(nil)

	options := []tls_client.HttpClientOption{
		tls_client.WithTimeoutSeconds(20),
		tls_client.WithClientProfile(profile),
		tls_client.WithInsecureSkipVerify(),
		tls_client.WithCookieJar(jar),
		tls_client.WithRandomTLSExtensionOrder(),
	}

	if USE_CHARLES {
		options = append(options,
			tls_client.WithCharlesProxy("127.0.0.1", "8888"),
		)
	} else if ip != "" {
		proxyURL := fmt.Sprintf("%s:%s@%s:%s", username, proxyPass, ip, port)

		if !strings.HasPrefix(ip, "http://") && !strings.HasPrefix(ip, "https://") {
			proxyURL = "http://" + proxyURL
		}

		options = append(options, tls_client.WithProxyUrl(proxyURL))
	}

	client, err := tls_client.NewHttpClient(tls_client.NewNoopLogger(), options...)
	if err != nil {
		return nil, err
	}

	return client, nil
}

func getRandomProxy() (string, string, string, string) {
	if len(proxies) == 0 {
		return "", "", "", ""
	}

	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	randomIndex := r.Intn(len(proxies))

	return parseProxy(proxies[randomIndex])
}

func parseProxy(proxyString string) (string, string, string, string) {
	parts := strings.Split(proxyString, ":")
	if len(parts) == 4 {
		return parts[0], parts[1], parts[2], parts[3]
	}
	return "", "", "", ""
}

func isSixDigits(s string) bool {
	match, _ := regexp.MatchString(`^\d{6}$`, s)
	return match
}

func getNickname(input string) string {
	parts := strings.Split(input, "@")
	return parts[0]
}

func addAccountAddress(email, password, name, phone, address1, address2 string) {
	fileName := "accountAddresses.txt"

	file, err := os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		return
	}
	defer file.Close()

	fmt.Fprintf(file, "%s:%s:%s:%s:%s:%s\n", email, password, name, phone, address1, address2)
}

func addAccount(email, password, originalEntry string) {
	fileName := "createdAccounts.txt"

	if OUTLOOK_EMAILS {
		fileName = "accountPool.txt"

		if Region != "US" {
			fileName = fmt.Sprintf("accountPool%s.txt", Region)
		}
	}

	file, err := os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		return
	}
	defer file.Close()

	fmt.Fprintf(file, "%s:%s\n", email, password)

	if SAVE_LINKED_MAILS && OUTLOOK_EMAILS {
		fileName2 := "linkedOutlooks.txt"

		file2, err2 := os.OpenFile(fileName2, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
		if err2 != nil {
			return
		}
		defer file2.Close()

		fmt.Fprintf(file2, "%s\n", originalEntry)
	}

	if RANDOM_TEMP_EMAILS {
		return
	}

	if OUTLOOK_EMAILS {
		removeLineFromFile("outlook.txt", originalEntry)
	} else {
		removeLineFromFile("EmailsToUse.txt", originalEntry)
	}
}

func removeLineFromFile(filename, lineToRemove string) error {
	dupLock.Lock()
	defer dupLock.Unlock()

	// Remove lineToRemove from 'emailsDup' global string slice
	for i, line := range emailsDup {
		if line == lineToRemove {
			emailsDup = slices.Delete(emailsDup, i, i+1)
			break
		}
	}

	// Write content of 'emailsDup' global string slice to filename, each element on 1 line
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create file %s: %w", filename, err)
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	for _, line := range emailsDup {
		if _, err := writer.WriteString(line + "\n"); err != nil {
			return fmt.Errorf("failed to write line to file: %w", err)
		}
	}

	if err := writer.Flush(); err != nil {
		return fmt.Errorf("failed to flush writer: %w", err)
	}

	return nil
}

func CheckEmail(currentEmail, lowerQuery string) bool {
	parts := strings.Split(lowerQuery, "@")
	if len(parts) != 2 {
		return false
	}

	localPart := strings.ReplaceAll(parts[0], ".", "")

	currentEmailNoDot := strings.ReplaceAll(currentEmail, ".", "")

	return strings.Contains(currentEmailNoDot, localPart)
}

func loadProxies() {
	var fileName string = "../" + RESI_TYPE

	if !USE_RESIS {
		fileName = "../isp.txt"
	}

	if _, err := os.Stat(fileName); os.IsNotExist(err) {
		fmt.Println("Error: proxy file not found.")
		return
	}

	file, err := os.Open(fileName)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" {
			proxies = append(proxies, line)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading file:", err)
		return
	}

	fmt.Printf("\n\nLoaded %d proxies.\n", len(proxies))
}

func loadOutlooks() {
	if _, err := os.Stat("outlook.txt"); os.IsNotExist(err) {
		fmt.Println("Error: 'outlook.txt' not found. Please create the file and add emails.")
		return
	}

	file, err := os.Open("outlook.txt")
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {

		line := strings.TrimSpace(scanner.Text())

		if line != "" {
			emails = append(emails, line)
			emailsDup = append(emailsDup, line)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading file:", err)
		return
	}

	if SHUFFLE_OUTLOOKS {
		rand.Shuffle(len(emails), func(i, j int) {
			emails[i], emails[j] = emails[j], emails[i]
		})
		rand.Shuffle(len(emailsDup), func(i, j int) {
			emailsDup[i], emailsDup[j] = emailsDup[j], emailsDup[i]
		})
	}

	fmt.Printf("Loaded %d outlooks from 'outlook.txt'.\n", len(emails))
}

func loadEmails() {
	if _, err := os.Stat("EmailsToUse.txt"); os.IsNotExist(err) {
		fmt.Println("Error: 'EmailsToUse.txt' not found. Please create the file and add emails.")
		return
	}

	file, err := os.Open("EmailsToUse.txt")
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {

		line := strings.TrimSpace(scanner.Text())

		if line != "" {
			emails = append(emails, line)
			emailsDup = append(emailsDup, line)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Error reading file:", err)
		return
	}

	fmt.Printf("Loaded %d emails from 'EmailsToUse.txt'.\n", len(emails))

	if DotMethodScaleFactor > 0 {
		var dotEmails []string = []string{}

		for i := range DotMethodScaleFactor {

			dotPosition := i + 1

			for _, email := range emails {
				if strings.Contains(email, "gmail") {
					newEmail := email[:dotPosition] + "." + email[dotPosition:]

					dotEmails = append(dotEmails, newEmail)
				}
			}
		}

		emails = append(emails, dotEmails...)

		rand.Shuffle(len(emails), func(i, j int) {
			emails[i], emails[j] = emails[j], emails[i]
		})

		fmt.Printf("Using dot method total emails is now %d\n", len(emails))
	}
}

func isSixtySecondsOld(t time.Time) bool {
	duration := time.Since(t)

	return duration >= 60*time.Second
}

func allDigits(s string) bool {
	for _, r := range s {
		if !unicode.IsDigit(r) {
			return false
		}
	}
	return true
}

func domainForRegion() string {
	query := strings.ToLower(Region)

	if query == "us" || query == "ca" {
		return "https://prod-na-api.popmart.com"
	}

	if query == "gb" ||
		query == "au" ||
		query == "br" ||
		query == "nz" ||
		query == "it" ||
		query == "at" ||
		query == "be" ||
		query == "hr" ||
		query == "dk" ||
		query == "ee" ||
		query == "fi" ||
		query == "fr" ||
		query == "de" ||
		query == "gr" ||
		query == "hu" ||
		query == "ie" ||
		query == "lv" ||
		query == "lt" ||
		query == "lu" ||
		query == "nl" ||
		query == "pl" ||
		query == "pt" ||
		query == "sk" ||
		query == "si" ||
		query == "es" ||
		query == "se" ||
		query == "ch" ||

		query == "id" ||
		query == "sg" ||
		query == "hk" ||
		query == "jp" ||
		query == "mo" ||
		query == "my" ||
		query == "kr" ||
		query == "tw" ||
		query == "vn" ||
		query == "ph" {

		return "https://prod-intl-api.popmart.com"
	}

	if query == "th" {
		return "https://prod-asia-api.popmart.com"
	}

	// US, CA
	return "https://prod-na-api.popmart.com"
}

func GetPopmartCountryData(site string) map[string]string {
	result := make(map[string]string)

	// Default values (same as US)
	result["namespace"] = "america"
	result["clientKey"] = "nw3b089qrgw9m7b7i"
	result["country"] = "US"
	result["projectId"] = "naus"
	result["lang"] = "en"

	// Determine country from site URL and set appropriate values
	if strings.Contains(site, "US") { // United States
		result["namespace"] = "america"
		result["clientKey"] = "nw3b089qrgw9m7b7i"
		result["country"] = "US"
		result["projectId"] = "naus"
		result["lang"] = "en"

	} else if strings.Contains(site, "CA") { // Canada
		result["namespace"] = "america"
		result["clientKey"] = "nw3b089qrgw9m7b7i"
		result["country"] = "CA"
		result["projectId"] = "naus"
		result["lang"] = "en"

	} else if strings.Contains(site, "BR") { // Brazil
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "BR"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "AU") { // Australia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "AU"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "NZ") { // New Zealand
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "NZ"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "AT") { // Austria
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "AT"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "BE") { // Belgium
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "BE"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "HR") { // Croatia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "HR"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "CZ") { // Czech Republic
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "CZ"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "DK") { // Denmark
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "DK"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "EE") { // Estonia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "EE"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "FI") { // Finland
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "FI"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "FR") { // France
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "FR"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "DE") { // Germany
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "DE"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "GR") { // Greece
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "GR"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "HU") { // Hungary
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "HU"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "IE") { // Ireland
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "IE"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "IT") { // Italy
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "IT"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "LV") { // Latvia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "LV"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "LT") { // Lithuania
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "LT"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "LU") { // Luxembourg
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "LU"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "NL") { // Netherlands
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "NL"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "PL") { // Poland
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "PL"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "PT") { // Portugal
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "PT"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "SK") { // Slovakia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "SK"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "SI") { // Slovenia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "SI"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "ES") { // Spain
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "ES"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "SE") { // Sweden
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "SE"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "CH") { // Switzerland
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "CH"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "GB") { // United Kingdom
		result["namespace"] = "eurasianuk"
		result["clientKey"] = "xzriem686i2i2dkwo"
		result["country"] = "GB"
		result["projectId"] = "uk"
		result["lang"] = "en"

	} else if strings.Contains(site, "HK") { // Hong Kong
		result["namespace"] = "hk"
		result["clientKey"] = "xzriem686i2i2dkwo"
		result["country"] = "HK"
		result["projectId"] = "hk"
		result["lang"] = "en"

	} else if strings.Contains(site, "ID") { // Indonesia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "ID"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "JP") { // Japan
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "JP"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "MO") { // Macao
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "MO"
		result["projectId"] = "eude"
		result["lang"] = "zh-hant"

	} else if strings.Contains(site, "MY") { // Malaysia
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "MY"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "PH") { // Philippines
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "PH"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "SG") { // Singapore
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "SG"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "KR") { // South Korea
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "KR"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "TW") { // Taiwan
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "TW"
		result["projectId"] = "eude"
		result["lang"] = "en"

	} else if strings.Contains(site, "TH") { // Thailand
		result["namespace"] = "thailand"
		result["clientKey"] = "dbaom9yv13gz80n3j"
		result["country"] = "TH"
		result["projectId"] = "thailand"
		result["lang"] = "th"

	} else if strings.Contains(site, "VN") { // Vietnam
		result["namespace"] = "eurasian"
		result["clientKey"] = "rmdxjisjk7gwykcix"
		result["country"] = "VN"
		result["projectId"] = "eude"
		result["lang"] = "en"
	}

	return result
}

func clearAndRetry() bool {
	if len(emailsDup) > 0 {
		fmt.Println("\n\n==============")
		fmt.Println("Restarting failures in 70 seconds")
		fmt.Println("==============")
		time.Sleep(70 * time.Second)

		emails = []string{}
		emails = append(emails, emailsDup...)

		return true
	} else {
		return false
	}
}

func findEmailIndex(targetEmail string) int {
	for i, email := range emails {
		if email == targetEmail {
			return i
		}
	}
	return 0
}

func SetIP(client tls_client.HttpClient, proxyStr string) string {
	if proxyStr == "" {
		generalLock.RLock()
		if publicIP != "" {
			currentIP := publicIP
			generalLock.RUnlock()
			return currentIP
		}
		generalLock.RUnlock()

		ip := GetPublicIP()

		if ip == "" {
			ip = GetIP(client)
		}

		generalLock.Lock()
		publicIP = ip
		generalLock.Unlock()

		return ip
	} else {
		realIpsLock.RLock()
		cachedIP, exists := realIps[proxyStr]
		realIpsLock.RUnlock()

		if exists && cachedIP != "" {
			return cachedIP
		} else {
			ip := GetProxyPublicIP(client)

			if ip == "" {
				ip = GetIP(client)
			}

			if ip != "" {
				realIpsLock.Lock()
				realIps[proxyStr] = ip
				realIpsLock.Unlock()
			}

			return ip
		}
	}
}

func GetIP(client tls_client.HttpClient) string {
	endPoint := "https://ip.justhyped.dev/ip"

	req, err := fhttp.NewRequest(fhttp.MethodGet, endPoint, nil)
	if err != nil {
		return ""
	}

	req.Header.Set("x-api-key", "52484c0e-b114-41ff-924b-53e27995d5a3")

	resp, err := client.Do(req)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return ""
	}

	var result map[string]string
	if err := json.Unmarshal(body, &result); err != nil {
		return ""
	}

	ip, exists := result["ip"]
	if !exists {
		return ""
	}

	return ip
}

type IPResponse struct {
	Query string `json:"query"`
}

func GetProxyPublicIP(client tls_client.HttpClient) string {
	req, err := fhttp.NewRequest(fhttp.MethodGet, "http://ip-api.com/json/", nil)
	if err != nil {
		return ""
	}

	resp, err := client.Do(req)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return ""
	}

	var ipResp IPResponse
	err = json.Unmarshal(body, &ipResp)
	if err != nil {
		return ""
	}

	return ipResp.Query
}

func GetPublicIP() string {
	response, err := http.Get("https://api.ipify.org")
	if err != nil {
		return ""
	}
	defer response.Body.Close()

	ip, err := io.ReadAll(response.Body)
	if err != nil {
		return ""
	}

	return string(ip)
}

const charset = "abcdefghijklmnopqrstuvwxyz0123456789"

func generateRandomUsername() string {
	firstName := randomFirstName()

	rngMuName.Lock()
	defer rngMuName.Unlock()

	suffixLength := randName.Intn(4) + 2

	var suffix strings.Builder
	suffix.Grow(suffixLength)

	for range suffixLength {
		suffix.WriteByte(charset[randName.Intn(len(charset))])
	}

	return firstName + suffix.String()
}

func randomFirstName() string {
	rngMuName.Lock()
	defer rngMuName.Unlock()

	firstName := commonFirstNames[randName.Intn(len(commonFirstNames))]

	return firstName
}

func randomLastName() string {
	rngMuName.Lock()
	defer rngMuName.Unlock()

	firstName := commonLastNames[randName.Intn(len(commonLastNames))]

	return firstName
}

var commonFirstNames []string = []string{
	"James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
	"David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
	"Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
	"Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
	"Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah",
	"Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Laura", "Jeffrey", "Sharon", "Ryan", "Cynthia",
	"Jacob", "Kathleen", "Gary", "Amy", "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen",
	"Stephen", "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
	"Frank", "Samantha", "Benjamin", "Katherine", "Gregory", "Christine", "Raymond", "Debra", "Samuel", "Rachel",
	"Patrick", "Catherine", "Alexander", "Carolyn", "Jack", "Janet", "Dennis", "Ruth", "Jerry", "Maria",
	"Tyler", "Heather", "Aaron", "Diane", "Henry", "Virginia", "Douglas", "Julie", "Jose", "Joyce",
	"Peter", "Victoria", "Adam", "Olivia", "Zachary", "Kelly", "Nathan", "Christina", "Walter", "Lauren",
	"Kyle", "Joan", "Harold", "Evelyn", "Carl", "Judith", "Jeremy", "Megan", "Keith", "Cheryl", "Roger", "Andrea",
	"Gerald", "Hannah", "Ethan", "Martha", "Arthur", "Jacqueline", "Terry", "Frances", "Christian", "Gloria",
	"Sean", "Ann", "Lawrence", "Teresa", "Austin", "Kathryn", "Joe", "Sara", "Noah", "Janice", "Jesse", "Jean",
	"Albert", "Alice", "Bryan", "Madison", "Billy", "Doris", "Bruce", "Abigail", "Willie", "Julia", "Jordan", "Judy",
	"Dylan", "Grace", "Alan", "Denise", "Ralph", "Amber", "Gabriel", "Marilyn", "Roy", "Beverly", "Juan", "Danielle",
	"Wayne", "Theresa", "Eugene", "Sophia", "Logan", "Marie", "Randy", "Diana", "Louis", "Brittany", "Russell", "Natalie",
	"Vincent", "Isabella", "Philip", "Charlotte", "Bobby", "Rose", "Johnny", "Alexis", "Bradley", "Kayla", "Earl", "Lori",
	"Victor", "Linda", "Martin", "Emma", "Ernest", "Mildred", "Phillip", "Stephanie", "Todd", "Jane", "Jared", "Clara",
	"Samuel", "Lucy", "Troy", "Ellie", "Tony", "Sophia", "Curtis", "Scarlett", "Allen", "Ellie", "Craig", "Elijah",
	"Arthur", "Penelope", "Derek", "Riley", "Shawn", "Liam", "Joel", "Aria", "Ronnie", "Isabella", "Oscar", "Amelia",
	"Jay", "Zoey", "Jorge", "Carter", "Ray", "Levi", "Jim", "Miles", "Jason", "Adrian", "Clifford", "Leah",
	"Wesley", "Nathaniel", "Max", "Hayden", "Clayton", "Jonathan", "Bryant", "Lucas", "Isaac", "Hudson",
	"Abby", "Connor", "Ezra", "Jaxon", "Theodore", "Gianna", "Sadie", "Eli", "Ella", "Grayson", "Kinsley",
	"Owen", "Avery", "Landon", "Stella", "Parker", "Nova", "Kayden", "Aubrey", "Josiah", "Claire", "Cooper",
	"Lillian", "Ryder", "Violet", "Lincoln", "Bella", "Carson", "Genesis", "Asher", "Mackenzie", "Easton",
	"Ivy", "Jace", "Hazel", "Micah", "Aurora", "Declan", "Savannah", "Beckett", "Sophie", "Sawyer", "Leilani",
	"Brody", "Valeria", "Charlie", "Peyton", "Mateo", "Layla", "Zane", "Melody", "Emmett", "Madeline", "Jonah",
	"Jade", "Xavier", "Brooklyn", "Maxwell", "Isabelle", "Harrison", "Cora", "Leo", "Eliza", "Rowan", "Anna",
	"Jameson", "Sadie", "Bennett", "Lydia", "Grant", "Alyssa", "Callum", "Natalie", "Kingston", "Sophia",
	"Felix", "Ruby", "Tobias", "Daisy", "Theo", "Adeline", "Ezekiel", "Emilia", "Hugo", "Olive", "Atticus",
	"Vivian", "Silas", "Luna", "Miles", "Autumn", "Camden", "Maeve", "Elliot", "Harper", "Everett", "Alice",
	"Bentley", "Clara", "Brady", "Ellie", "Luca", "Aurora", "Dominic", "Scarlett", "Maximus", "Aria", "Walker",
	"Zoey", "River", "Bella", "Romeo", "Violet", "Finn", "Aubrey", "Nico", "Addison", "Elias", "Eleanor", "Aiden",
	"Layla", "Rowen", "Willow", "Judah", "Naomi", "Enzo", "Penelope", "Malachi", "Maya", "Rhett", "Eva",
	"Kai", "Sienna", "Archer", "Eliana", "Beau", "Daphne", "Dax", "Rose", "Remy", "Avery", "August", "Faith",
	"Emery", "Emerson", "Reid", "Madelyn", "Tucker", "Wren", "Zander", "Gia", "Griffin", "Serenity", "Jayce",
	"Iris", "Maddox", "Briar", "Zayne", "Carmen", "Ellis", "Hope", "Cash", "Fiona", "Emory", "Olivia", "Bryce",
}

var commonLastNames []string = []string{
	"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
	"Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
	"Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
	"Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
	"Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
	"Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
	"Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
	"Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
	"Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
	"Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
	"Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes",
	"Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
	"Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
	"Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro", "Marshall", "Owens",
	"Harrison", "Fernandez", "Mcdonald", "Woods", "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen",
	"Freeman", "Webb", "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
	"Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt", "Hicks",
	"Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd", "Rose", "Stone", "Salazar", "Fox",
	"Warren", "Mills", "Meyer", "Rice", "Schmidt", "Garza", "Daniels", "Ferguson", "Nichols", "Stephens",
	"Soto", "Weaver", "Ryan", "Gardner", "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins",
	"Arnold", "Pierce", "Vazquez", "Hansen", "Peters", "Santos", "Hart", "Bradley", "Knight", "Elliott",
	"Cunningham", "Duncan", "Armstrong", "Hudson", "Carroll", "Lane", "Riley", "Andrews", "Alvarado", "Ray",
	"Delgado", "Berry", "Perkins", "Hoffman", "Johnston", "Matthews", "Pena", "Richards", "Contreras", "Willis",
	"Carpenter", "Lawrence", "Sandoval", "Guerrero", "George", "Chapman", "Rios", "Estrada", "Ortega", "Watkins",
	"Greene", "Nunez", "Wheeler", "Valdez", "Harper", "Burke", "Larson", "Santiago", "Maldonado", "Morrison",
	"Franklin", "Carlson", "Austin", "Dominguez", "Carr", "Lawson", "Jacobs", "O'Brien", "Lynch", "Singh",
	"Vega", "Bishop", "Montgomery", "Oliver", "Jensen", "Harvey", "Williamson", "Gilbert", "Dean", "Sims",
	"Espinoza", "Howell", "Li", "Wong", "Reid", "Hanson", "Le", "McCoy", "Garrett", "Burton",
	"Fuller", "Wang", "Weber", "Welch", "Rojas", "Lucas", "Marquez", "Fields", "Park", "Yang",
	"Little", "Banks", "Padilla", "Day", "Walsh", "Bowman", "Schultz", "Luna", "Fowler", "Mejia",
	"Davidson", "Acosta", "Brewer", "May", "Holland", "Juarez", "Newman", "Pearson", "Curtis", "Cortez",
	"Douglas", "Schneider", "Joseph", "Barrett", "Navarro", "Figueroa", "Keller", "Avila", "Wade", "Molina",
	"Stanley", "Hopkins", "Campos", "Barnett", "Bates", "Chambers", "Caldwell", "Beck", "Lambert", "Miranda",
	"Byrd", "Craig", "Ayala", "Lowe", "Frazier", "Powers", "Neal", "Leonard", "Gregory", "Carrillo",
	"Sutton", "Fleming", "Rhodes", "Shelton", "Schwartz", "Norris", "Jennings", "Watts", "Duran", "Walters",
	"Cohen", "McDaniel", "Moran", "Parks", "Steele", "Vaughn", "Becker", "Holt", "DeLeon", "Barker",
	"Terry", "Hale", "Leon", "Hail", "Rich", "Clarkson", "Lopez", "Ryan", "Fisher", "Cross",
	"Hardy", "Shields", "Savage", "Hodges", "Ingram", "Delacruz", "Cervantes", "Wyatt", "Dominguez", "Montoya",
	"Love", "Robbins", "Salinas", "Yates", "Duarte", "Kirk", "Ford", "Pitt", "Bartlett", "Valenzuela",
}

var stateMap = map[string]StateInfo{
	"Alabama":        {"Alabama", "AL"},
	"Alaska":         {"Alaska", "AK"},
	"Arizona":        {"Arizona", "AZ"},
	"Arkansas":       {"Arkansas", "AR"},
	"California":     {"California", "CA"},
	"Colorado":       {"Colorado", "CO"},
	"Connecticut":    {"Connecticut", "CT"},
	"Delaware":       {"Delaware", "DE"},
	"Florida":        {"Florida", "FL"},
	"Georgia":        {"Georgia", "GA"},
	"Hawaii":         {"Hawaii", "HI"},
	"Idaho":          {"Idaho", "ID"},
	"Illinois":       {"Illinois", "IL"},
	"Indiana":        {"Indiana", "IN"},
	"Iowa":           {"Iowa", "IA"},
	"Kansas":         {"Kansas", "KS"},
	"Kentucky":       {"Kentucky", "KY"},
	"Louisiana":      {"Louisiana", "LA"},
	"Maine":          {"Maine", "ME"},
	"Maryland":       {"Maryland", "MD"},
	"Massachusetts":  {"Massachusetts", "MA"},
	"Michigan":       {"Michigan", "MI"},
	"Minnesota":      {"Minnesota", "MN"},
	"Mississippi":    {"Mississippi", "MS"},
	"Missouri":       {"Missouri", "MO"},
	"Montana":        {"Montana", "MT"},
	"Nebraska":       {"Nebraska", "NE"},
	"Nevada":         {"Nevada", "NV"},
	"New Hampshire":  {"New Hampshire", "NH"},
	"New Jersey":     {"New Jersey", "NJ"},
	"New Mexico":     {"New Mexico", "NM"},
	"New York":       {"New York", "NY"},
	"North Carolina": {"North Carolina", "NC"},
	"North Dakota":   {"North Dakota", "ND"},
	"Ohio":           {"Ohio", "OH"},
	"Oklahoma":       {"Oklahoma", "OK"},
	"Oregon":         {"Oregon", "OR"},
	"Pennsylvania":   {"Pennsylvania", "PA"},
	"Rhode Island":   {"Rhode Island", "RI"},
	"South Carolina": {"South Carolina", "SC"},
	"South Dakota":   {"South Dakota", "SD"},
	"Tennessee":      {"Tennessee", "TN"},
	"Texas":          {"Texas", "TX"},
	"Utah":           {"Utah", "UT"},
	"Vermont":        {"Vermont", "VT"},
	"Virginia":       {"Virginia", "VA"},
	"Washington":     {"Washington", "WA"},
	"West Virginia":  {"West Virginia", "WV"},
	"Wisconsin":      {"Wisconsin", "WI"},
	"Wyoming":        {"Wyoming", "WY"},
}

func GetStateInfo(input string) StateInfo {
	if Region == "CA" {
		return StateInfo{"Ontario", "ON"}
	}

	normalizedInput := strings.ToUpper(input)
	for key, value := range stateMap {
		if strings.ToUpper(key) == normalizedInput || value.ProvinceCode == normalizedInput {
			return value
		}
	}
	return StateInfo{"", ""}
}

type StateInfo struct {
	ProvinceName string
	ProvinceCode string
}

func FullCountryName(countryCode string) string {
	name, ok := countryMap[countryCode]

	if ok {
		return name
	}

	return "United States"
}

var countryMap = map[string]string{
	"US": "United States",
	"CA": "Canada",
	"BR": "Brazil",
	"AU": "Australia",
	"NZ": "New Zealand",
	"AT": "Austria",
	"BE": "Belgium",
	"HR": "Croatia",
	"CZ": "Czech Republic",
	"DK": "Denmark",
	"EE": "Estonia",
	"FI": "Finland",
	"FR": "France",
	"DE": "Germany",
	"GR": "Greece",
	"HU": "Hungary",
	"IE": "Ireland",
	"IT": "Italy",
	"LV": "Latvia",
	"LT": "Lithuania",
	"LU": "Luxembourg",
	"NL": "Netherlands",
	"PL": "Poland",
	"PT": "Portugal",
	"SK": "Slovakia",
	"SI": "Slovenia",
	"ES": "Spain",
	"SE": "Sweden",
	"CH": "Switzerland",
	"GB": "United Kingdom",
	"HK": "Hong Kong",
	"ID": "Indonesia",
	"JP": "Japan",
	"MO": "Macao",
	"MY": "Malaysia",
	"PH": "Philippines",
	"SG": "Singapore",
	"KR": "South Korea",
	"TW": "Taiwan",
	"TH": "Thailand",
	"VN": "Vietnam",
}

const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func Random3CharString() string {
	b := make([]byte, 3)
	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	for i := range b {
		b[i] = letters[randProfile.Intn(len(letters))]
	}
	return string(b)
}

func RandomCharString() string {
	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	return string(letters[randProfile.Intn(len(letters))])
}

func generateRandomAddress2() string {
	// Define prefixes for address 2
	prefixes := []string{
		"APT", "APT", "APT", // More weight for APT
		"Unit", "Unit", // More weight for Unit
		"STE", "Suite",
		"BLD", "Building",
		"FL", "Floor",
		"RM", "Room",
		"LOT", "Lot",
		"TRLR", "Trailer",
		"BSMT", "Basement",
		"FRNT", "Front",
		"REAR", "Rear",
		"UPPR", "Upper",
		"LOWR", "Lower",
		"#",
	}

	// Define suffix letters for variations like 2a, 6c, etc.
	suffixLetters := []string{"", "", "", "", "A", "B", "C", "D", "E", "F"} // More weight for no suffix

	// Lock the mutex to ensure thread safety
	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	prefix := prefixes[randProfile.Intn(len(prefixes))]
	number := randProfile.Intn(99) + 1 // Random number from 1 to 99
	suffix := suffixLetters[randProfile.Intn(len(suffixLetters))]

	// Create the address string
	if prefix == "#" {
		return fmt.Sprintf("#%d%s", number, suffix)
	} else {
		return fmt.Sprintf("%s %d%s", prefix, number, suffix)
	}
}

func randomDigits(length int) string {
	digits := "0123456789"
	result := make([]byte, length)

	rngMuProfile.Lock()
	defer rngMuProfile.Unlock()

	for i := 0; i < length; i++ {
		result[i] = digits[randProfile.Intn(len(digits))]
	}

	return string(result)
}
