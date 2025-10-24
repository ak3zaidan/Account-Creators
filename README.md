# Account Creators

- The best OS Account creators on Github
- 20 Modules for the top sites, everything works with no issues
- I built these over the past few months and expierence no bugs with them
- All modules follow a common pattern, input emails into the "emailsToUse.txt" file, fill out top globals in main.py then run
- Check the imports at the top for what dep you need
- NoDriver, SD, and Camoufox all used
- Target module runs fully unflagged to Shape bot detection (not on remote servers though as the hardware is detected)

# Modules:

- **Ali Express**:
  - Works great, requires IMAP and unique emails
- **Amazon**:
  - Works great, requires IMAP and unique emails
  - Requires SMS API keys
  - Requires chromium with CapSolver extension to solve AWS captcha
  - The module can auto setup billing/shipping info on each account after signup
- **BestBuy**
  - Works best using ISP - Fast Generation
  - Works great with catchall domain or unique emails
  - Optionally include IMAP to verify accounts
- **Costco**
  - Works very smooth
  - Requires IMAP to verify accounts
  - Accounts do not have memberships
- **FootLocker FLX**
  - Works great for unique emails and catchall domain
- **GOAT**
  - Works very smooth
  - Requires IMAP to email verify accounts
- **iCloud HME**
  - Generate/Read iCloud HME for Apple plus accounts
  - 5 gen limit per hour and 750 total
- **Levi**
  - Works great
- **Nike**
  - Works great and offers email+sms verification
  - Requires IMAP to verify accounts
  - Optionally SMS verify accounts using DaisySMS/SMSpool
- **Outlook Forward**
  - Forward a list of outlooks to a destination email using outlook mailbox rules
  - Only limitation is Junk emails do not forward
- **Pkc Japan**
  - Works good using high quality Japan resis
  - Requires IMAP to verify accounts
  - Works best using Gmails
- **Pokemon**
  - Works amazing for Pokemon US/GB
- **Popmart**
  - Go Request based
  - Supports every region
  - Requires a list of emails or list of outlooks with refresh tokens
  - In house TD solver
  - Supports every region
  - See my "Trust Decision" repo for the antibot solver
- **Sams Club**
  - Works great with resis
- **Scotty Cameron**
  - Works very smooth
  - Requires IMAP to verify accounts
  - Manual solve
- **Target**
  - Works amazing - fully unflagged - no device bans after tens of thousands of sessions
  - Chromium required (I'm using chromium version 104 on macOS)
  - IMAP not really needed, only 1/5 sessions requires email verification
- **Topps**
  - Works only high quality resis
  - Requires IMAP for verifcation
- **Walmart**
  - Go request based
  - PX unflagged sessions
  - Optimal on 2 threads
  - SMS api keys required
  - Each unique Catchall limited to 20 sessions per hour
  - Recommended to use real-unique emails
 







