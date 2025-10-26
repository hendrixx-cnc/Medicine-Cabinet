# Publishing to Chrome Web Store - Complete Guide

## Prerequisites

1. **Google Account** with payment method
2. **Developer Account** ($5 one-time fee)
3. **Extension ready** with all assets

## Step-by-Step Publishing

### 1. Prepare Extension Package

```bash
cd chrome-extension

# Create distribution ZIP
zip -r ../medicine-cabinet-chrome-v1.0.0.zip . \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "README.md" \
  -x "quick_start.md" \
  -x "publishing.md" \
  -x "generate_icons.py" \
  -x "__pycache__/*"
```

### 2. Create Required Assets

#### Screenshots (Required)
- **Size**: 1280x800 or 640x400 pixels
- **Format**: PNG or JPEG
- **Minimum**: 1 screenshot
- **Recommended**: 3-5 screenshots

Capture:
- Extension popup with loaded capsules
- Context injection in action (ChatGPT, GitHub)
- Detail modal view
- Settings/features

#### Promotional Images (Optional but Recommended)

**Small Tile** (Required for featured placement):
- Size: 440x280 pixels
- Format: PNG or JPEG
- Content: Logo + tagline

**Large Tile** (Optional):
- Size: 920x680 pixels
- Format: PNG or JPEG

**Marquee** (Optional):
- Size: 1400x560 pixels
- Format: PNG or JPEG

### 3. Register as Developer

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Sign in with Google Account
3. Pay $5 one-time developer registration fee
4. Agree to terms and policies

### 4. Create New Item

1. Click **"New Item"** button
2. Upload `medicine-cabinet-chrome-v1.0.0.zip`
3. Wait for upload and validation

### 5. Fill Store Listing

#### Product Details

**Name**: `Medicine Cabinet`

**Summary** (132 chars max):
```
AI memory management for developers - Load capsules & tablets to inject context into GitHub, ChatGPT, Claude, and more.
```

**Description** (16,000 chars max):
```markdown
# Medicine Cabinet - AI Memory for Developers

Transform how you work with AI assistants by maintaining persistent context across all your development tools.

## What is Medicine Cabinet?

Medicine Cabinet is a revolutionary memory management system for AI-assisted development. Load "Capsules" (working memory) and "Tablets" (long-term memory) to provide rich context to any AI assistant or development platform.

## Key Features

✅ **Smart Context Injection**
- One-click injection into ChatGPT, Claude, Gemini, and Copilot
- Automatic detection of GitHub issues, PRs, and Stack Overflow
- Intelligent formatting per platform

✅ **Binary Format Support**
- Native parsing of .auractx (Capsule) files
- Native parsing of .auratab (Tablet) files
- No external dependencies or cloud services

✅ **Privacy First**
- 100% local storage - no data leaves your browser
- No tracking, no analytics, no external requests
- Open source and auditable

✅ **Cross-Platform**
- Works on all Chromium browsers (Chrome, Edge, Brave, Opera)
- Compatible with GitHub, Stack Overflow, ChatGPT, Claude, Gemini, Copilot, Poe
- Automatic clipboard fallback for unsupported sites

## How It Works

1. **Create Memory Files** using the Python CLI or your preferred method
2. **Load into Extension** via the popup interface
3. **Set Active Capsule** to specify current working context
4. **Inject Context** with one click while working on any supported platform

## Use Cases

- **GitHub Collaboration**: Share project context in issues and PRs
- **AI Pair Programming**: Provide comprehensive background to ChatGPT/Claude
- **Code Reviews**: Include relevant architectural decisions
- **Documentation**: Reference past implementations
- **Bug Fixing**: Share historical context about the codebase

## Supported Platforms

- GitHub (issues, PRs, discussions)
- Stack Overflow (questions, answers)
- ChatGPT
- Claude AI
- Google Gemini
- Microsoft Copilot
- Poe
- Any site via clipboard

## Part of a Complete Ecosystem

Medicine Cabinet is one component of a comprehensive AI development toolkit:

- **Python Library**: Create and manage capsules/tablets programmatically
- **CLI Tools**: Command-line interface for power users
- **VS Code Extension**: (Coming soon) Seamless IDE integration
- **Browser Extensions**: Chrome, Safari, Firefox support

## Privacy & Security

- All data stored locally using browser's storage API
- No external servers or cloud dependencies
- No user tracking or analytics
- Minimal permissions (only what's necessary)
- Open source - audit the code yourself

## Get Started

1. Install the extension
2. Download the Python library: `pip install medicine-cabinet`
3. Create your first capsule: `medicine-cabinet capsule create "MyProject" "Description"`
4. Load it in the extension and start injecting context!

## Links

- Documentation: https://github.com/hendrixx-cnc/Medicine-Cabinet
- Python Library: https://github.com/hendrixx-cnc/Medicine-Cabinet
- Related Projects: Orkestra, AURA, The Quantum Self

Created by Todd Hendricks (@hendrixx-cnc)
```

#### Category

Select: **Productivity** or **Developer Tools**

#### Language

Primary: **English**

#### Privacy Policy

If you don't collect user data (we don't), you can state:

```
Medicine Cabinet Privacy Policy

Last Updated: October 26, 2025

Data Collection:
Medicine Cabinet does not collect, store, or transmit any user data. All capsules and tablets loaded into the extension are stored locally in your browser using the chrome.storage.local API.

Third-Party Services:
This extension does not integrate with or send data to any third-party services.

Permissions:
- storage: Used to persist loaded capsules/tablets locally
- activeTab: Used to inject context into the current page when explicitly requested by the user
- host_permissions: Limited to specific sites where injection is supported

User Control:
Users have complete control over their data:
- All files are loaded explicitly by the user
- Data can be cleared by removing the extension
- No automatic data collection or transmission occurs

Contact:
For privacy concerns, contact: [your-email]

GitHub: https://github.com/hendrixx-cnc/Medicine-Cabinet
```

Host this on GitHub Pages or your website.

#### Upload Assets

- Screenshots (1-5 images)
- Small promotional tile (440x280)
- Icon already in manifest.json

### 6. Distribution Settings

**Visibility**: 
- Public (recommended)
- Unlisted (only via direct link)
- Private (for testing)

**Geographic Distribution**: Worldwide

**Pricing**: Free

### 7. Review & Submit

1. Preview your listing
2. Click **"Submit for Review"**
3. Wait 1-5 business days for review

## After Approval

### Update Version

1. Increment version in `manifest.json`
2. Create new ZIP
3. Upload to existing item (don't create new)
4. Submit for review

### Monitor Stats

Dashboard shows:
- Weekly installs
- Active users
- Ratings and reviews
- Crash reports

## Common Rejection Reasons

❌ **Minimal Functionality**: Ensure robust features  
❌ **Misleading Description**: Be accurate and clear  
❌ **Permission Issues**: Only request necessary permissions  
❌ **Privacy Policy**: Required if any data collection  
❌ **Broken Features**: Test thoroughly before submission  
❌ **Copyright Issues**: Use only original or licensed assets  

## Tips for Approval

✅ Clear, professional screenshots  
✅ Detailed, accurate description  
✅ Minimal permissions  
✅ No broken links  
✅ Professional icon and graphics  
✅ Works as described  
✅ Clear privacy policy  

## Marketing After Launch

1. **GitHub README**: Link to Chrome Web Store
2. **Product Hunt**: Launch announcement
3. **Reddit**: r/chrome, r/ChromeExtensions, r/programming
4. **Twitter/LinkedIn**: Share with screenshots
5. **Dev.to**: Write tutorial article
6. **YouTube**: Create demo video

## Support

Respond to user reviews and provide support:
- Monitor Chrome Web Store reviews
- Create GitHub Issues for bug reports
- Update regularly with fixes and features

## Analytics (Optional)

If you add analytics later:
1. Update privacy policy
2. Request additional permissions
3. Submit for re-review
4. Clearly inform users

---

**Important**: Chrome Web Store reviews can take 1-5 days. Plan accordingly and don't submit right before a deadline!
