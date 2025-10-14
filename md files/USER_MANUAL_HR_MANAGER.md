# Resumify - HR Manager / Company Admin User Manual

**Version:** 1.0
**Last Updated:** October 2025
**Role:** Company Administrator (HR Manager)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Managing Job Postings](#managing-job-postings)
5. [Candidate Management](#candidate-management)
6. [Resume Analysis](#resume-analysis)
7. [Interview Scheduling](#interview-scheduling)
8. [Team Management](#team-management)
9. [Reports & Analytics](#reports-analytics)
10. [Company Settings](#company-settings)
11. [Best Practices](#best-practices)

---

## Introduction

### What is an HR Manager / Company Admin?

As a **Company Administrator**, you are the primary HR manager for your organization in Resumify. You have the authority to:

✅ Post and manage job openings
✅ Review and analyze candidate resumes
✅ Schedule and track interviews
✅ Manage your recruitment team
✅ Generate hiring reports and analytics
✅ Configure company-specific settings

**Your Role:** You oversee the entire recruitment process for your company.

---

## Getting Started

### First-Time Login

**Step 1: Access Your Account**
1. Navigate to: `https://your-company.resumify.com`
2. Enter credentials provided by your Super Admin:
   - Username: `your_username`
   - Password: `temporary_password`
3. You'll be prompted to change your password on first login

**Step 2: Complete Your Profile**
```
Profile → Edit Profile
```

Fill in:
- **Full Name:** John Smith
- **Job Title:** HR Manager
- **Department:** Human Resources
- **Contact Email:** john.smith@company.com
- **Phone:** +1-555-0123
- **Profile Photo:** Upload professional photo

**Step 3: Set Up Two-Factor Authentication (Recommended)**
```
Profile → Security → Enable 2FA
```
1. Scan QR code with authenticator app
2. Enter verification code
3. Save backup codes securely

**Step 4: Configure Email Notifications**
```
Profile → Notifications
```

Choose which notifications you want to receive:
- [x] New candidate applications
- [x] Interview reminders
- [x] Team member actions
- [ ] Daily summary emails
- [x] System updates

---

## Dashboard Overview

### Main Dashboard

When you log in, you'll see your **HR Dashboard** with:

#### 1. **Quick Stats Panel**

```
┌─────────────────────────────────────┐
│ Active Job Postings        12       │
│ New Applications Today     8        │
│ Interviews This Week       15       │
│ Positions Filled MTD       3        │
└─────────────────────────────────────┘
```

#### 2. **Recent Applications**
View the 10 most recent candidate applications:
- Candidate name
- Position applied for
- Match score
- Application date
- Status (New, Reviewing, Shortlisted, Rejected)

#### 3. **Upcoming Interviews**
Calendar view of scheduled interviews:
- Date and time
- Candidate name
- Position
- Interviewer assigned
- Interview type (Phone, Video, In-person)

#### 4. **Pipeline Overview**
Visual funnel showing:
```
Applications (125) →
Screening (45) →
Interviewing (20) →
Offers (5) →
Hired (2)
```

#### 5. **Quick Actions**
- **Post New Job** - Create job opening
- **Review Resumes** - Analyze new applications
- **Schedule Interview** - Book interview slot
- **Add Team Member** - Invite recruiter

---

## Managing Job Postings

### Creating a New Job Posting

**Navigate to:** `Jobs → Create New Job`

#### Step 1: Basic Information

| Field | Description | Example |
|-------|-------------|---------|
| **Job Title*** | Position name | Senior Python Developer |
| **Department*** | Business unit | Engineering |
| **Location*** | Office location | San Francisco, CA / Remote |
| **Employment Type*** | Full-time/Part-time/Contract | Full-time |
| **Experience Level*** | Entry/Mid/Senior | Senior |
| **Salary Range** | Compensation (optional) | $120k - $150k |

#### Step 2: Job Description

**Job Summary:**
```
We are seeking an experienced Python Developer to join our
growing engineering team. You will be responsible for building
scalable web applications and APIs.
```

**Key Responsibilities:**
- Develop and maintain Python-based applications
- Design and implement RESTful APIs
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews

**Required Qualifications:**
- 5+ years Python development experience
- Strong knowledge of FastAPI or Django
- Experience with PostgreSQL
- Git version control proficiency
- Bachelor's degree in Computer Science

**Preferred Qualifications:**
- AWS/Azure cloud experience
- Docker and Kubernetes
- CI/CD pipeline experience
- Agile methodology experience

#### Step 3: Skills & Requirements

**Required Skills:** (Add tags)
```
[Python] [FastAPI] [PostgreSQL] [Git] [REST APIs]
```

**Preferred Skills:**
```
[Docker] [AWS] [Kubernetes] [Redis] [CI/CD]
```

**Minimum Education:**
- [ ] High School
- [ ] Associate Degree
- [x] Bachelor's Degree
- [ ] Master's Degree
- [ ] PhD

**Years of Experience:**
```
Minimum: 5 years
Preferred: 7+ years
```

#### Step 4: Application Settings

**Application Deadline:**
- [ ] No deadline
- [x] Set deadline: November 30, 2025

**Auto-Screen Candidates:**
- [x] Enable AI resume screening
- [x] Auto-reject candidates below 60% match
- [x] Auto-shortlist candidates above 85% match

**Application Questions:** (Optional)
1. Why are you interested in this position?
2. What is your salary expectation?
3. When can you start?

#### Step 5: Publish

- **Preview** - Review job posting
- **Save as Draft** - Save for later
- **Publish** - Make job live

**After Publishing:**
- Job appears on company career page
- Unique application URL generated
- Auto-screening starts for new applications

### Managing Existing Jobs

**View All Jobs:** `Jobs → View All`

**Filter Options:**
- Status: Active, Draft, Closed, Expired
- Department: All, Engineering, Sales, Marketing
- Date Posted: Last 7 days, Last 30 days, Custom range

**Job Actions:**

| Action | Description |
|--------|-------------|
| **Edit** | Modify job details |
| **Duplicate** | Create similar job posting |
| **Close** | Stop accepting applications |
| **Archive** | Move to archive (no longer visible) |
| **View Analytics** | See job performance metrics |
| **Share** | Get shareable link or embed code |

### Job Performance Analytics

**View Metrics:** `Jobs → [Job Name] → Analytics`

**Key Metrics:**
```
┌────────────────────────────────────┐
│ Views:              1,245          │
│ Applications:         87           │
│ Conversion Rate:     7.0%          │
│ Avg Match Score:     72%           │
│ Time to Fill:        23 days       │
│ Applicant Quality:   High          │
└────────────────────────────────────┘
```

**Application Funnel:**
```
87 Applications →
52 Screened (60%) →
18 Interviewing (21%) →
5 Offers (6%) →
2 Hired (2%)
```

**Source Tracking:**
- Direct: 35%
- LinkedIn: 25%
- Indeed: 20%
- Company Website: 15%
- Referral: 5%

---

## Candidate Management

### Viewing Candidates

**Navigate to:** `Candidates → All Candidates`

**View Options:**
- **List View** - Detailed table
- **Card View** - Visual cards
- **Pipeline View** - Kanban board

### Candidate List Columns

| Column | Description |
|--------|-------------|
| Name | Candidate full name |
| Position | Job applied for |
| Match Score | AI-calculated fit (0-100%) |
| Status | Current stage |
| Applied Date | When they applied |
| Last Activity | Recent action |
| Actions | Quick actions menu |

### Filtering Candidates

**Filter By:**
- **Status:** New, Screening, Shortlisted, Interviewing, Offer, Hired, Rejected
- **Job Position:** Filter by specific job
- **Match Score:** >90%, 80-90%, 70-80%, <70%
- **Date Range:** Last 7/30/90 days
- **Skills:** Python, Java, etc.
- **Experience:** 0-2, 3-5, 6-10, 10+ years
- **Education:** Bachelor's, Master's, PhD

**Advanced Search:**
```
Search by: Name, Email, Phone, Skills, Education, Company
```

### Reviewing a Candidate

**Click on candidate name to open profile:**

#### **Candidate Profile Overview**

**1. Header Section**
```
┌──────────────────────────────────────────────────────┐
│  [Photo]  John Doe                    Match: 87%     │
│           Senior Python Developer                     │
│           john.doe@email.com | +1-555-0199           │
│           San Francisco, CA                           │
│                                                       │
│  [Shortlist] [Schedule Interview] [Reject] [Notes]   │
└──────────────────────────────────────────────────────┘
```

**2. AI Match Analysis**

```
Overall Match: 87% ⭐⭐⭐⭐⭐

✅ Skills Match: 92%
   Required: Python, FastAPI, PostgreSQL ✓
   Bonus: Docker ✓, AWS ✓

✅ Experience: 90%
   7 years experience (Required: 5+)

✅ Education: 85%
   Bachelor's in Computer Science ✓

❌ Location: 60%
   Candidate: San Francisco (Remote possible)
   Job: New York / Remote
```

**3. Resume Summary (AI-Generated)**
```
Experienced Python developer with 7 years in web application development.
Strong background in FastAPI, Django, and cloud technologies. Previously
worked at Tech Corp and StartupXYZ building scalable microservices.
Holds Bachelor's degree in Computer Science.
```

**4. Work Experience**
```
Senior Python Developer
Tech Corp | Jan 2020 - Present (3 years)
- Led development of microservices architecture
- Reduced API response time by 40%
- Mentored junior developers

Python Developer
StartupXYZ | Jun 2018 - Dec 2019 (1.5 years)
- Built RESTful APIs using FastAPI
- Implemented CI/CD pipelines
```

**5. Education**
```
Bachelor of Science in Computer Science
University of Technology | 2014 - 2018
GPA: 3.8/4.0
```

**6. Skills**
```
Programming: Python ⭐⭐⭐⭐⭐ | JavaScript ⭐⭐⭐⭐
Frameworks: FastAPI ⭐⭐⭐⭐⭐ | Django ⭐⭐⭐⭐ | React ⭐⭐⭐
Databases: PostgreSQL ⭐⭐⭐⭐ | MongoDB ⭐⭐⭐ | Redis ⭐⭐⭐⭐
Tools: Docker ⭐⭐⭐⭐ | Kubernetes ⭐⭐⭐ | Git ⭐⭐⭐⭐⭐
```

**7. Certifications**
- AWS Certified Developer - Associate (2022)
- Python Professional Certification (2021)

**8. Languages**
- English: Native
- Spanish: Intermediate

### Candidate Actions

#### **1. Shortlist Candidate**
```
Actions → Shortlist
```
- Moves to "Shortlisted" status
- Sends notification to team
- Appears in shortlist dashboard

#### **2. Reject Candidate**
```
Actions → Reject
```
- Select rejection reason:
  - [ ] Insufficient experience
  - [ ] Skills mismatch
  - [ ] Location constraints
  - [ ] Salary expectations
  - [ ] Position filled
  - [ ] Other: ___________

- [ ] Send rejection email
- [ ] Keep in talent pool for future

**Rejection Email Template:**
```
Dear [Candidate Name],

Thank you for applying for the [Position] role at [Company Name].

After careful review, we have decided to move forward with other
candidates whose qualifications more closely match our current needs.

We appreciate your interest and encourage you to apply for future
opportunities that match your skills.

Best regards,
[Your Name]
HR Manager
```

#### **3. Add Notes**
```
Actions → Add Note
```
- Private notes (visible to team only)
- Tags: #strong-communicator #culture-fit #negotiable
- Attach files
- @mention team members

**Example Note:**
```
@Sarah - Great candidate! Strong technical skills and excellent
communication. Salary expectation is $135k which is within budget.
Recommend scheduling technical interview ASAP.

#recommended #technical-skills #good-fit
```

#### **4. Compare Candidates**
```
Select multiple candidates → Compare
```

Side-by-side comparison:
```
┌─────────────┬───────────┬───────────┬───────────┐
│ Metric      │ John Doe  │ Jane Smith│ Bob Jones │
├─────────────┼───────────┼───────────┼───────────┤
│ Match Score │ 87%       │ 92%       │ 78%       │
│ Experience  │ 7 years   │ 5 years   │ 10 years  │
│ Education   │ Bachelor's│ Master's  │ Bachelor's│
│ Salary Exp  │ $135k     │ $125k     │ $150k     │
│ Availability│ 2 weeks   │ 1 month   │ Immediate │
└─────────────┴───────────┴───────────┴───────────┘
```

---

## Resume Analysis

### AI Resume Parsing

**Automatic Extraction:**

When a candidate uploads a resume, Resumify automatically extracts:

✅ **Personal Information**
- Name, Email, Phone, Location
- LinkedIn profile, Portfolio links

✅ **Work Experience**
- Company names and dates
- Job titles and responsibilities
- Achievements and metrics

✅ **Education**
- Degrees and institutions
- Graduation dates
- GPA (if mentioned)

✅ **Skills**
- Technical skills
- Soft skills
- Tools and technologies
- Certifications

✅ **Additional Info**
- Languages spoken
- Certifications
- Publications
- Awards

### Skills Matching

**How It Works:**

1. **Job Requirements** (What you need)
   ```
   Required: Python, FastAPI, PostgreSQL, Git
   Preferred: Docker, AWS, Kubernetes
   ```

2. **Candidate Skills** (What they have)
   ```
   Python ✓, FastAPI ✓, PostgreSQL ✓, Git ✓
   Docker ✓, AWS ✓, React (not required)
   ```

3. **Match Calculation**
   ```
   Required Skills: 4/4 = 100%
   Preferred Skills: 2/3 = 67%
   Overall Match: 87%
   ```

### Resume Quality Score

**Resumify analyzes resume quality:**

```
Resume Quality: 8.5/10 ⭐⭐⭐⭐

✅ Well-structured format
✅ Clear work history
✅ Quantified achievements
✅ No spelling errors
⚠️  Missing portfolio link
✅ Professional summary included
```

### Bulk Resume Upload

**Upload Multiple Resumes:**
```
Candidates → Bulk Upload
```

1. Select job position
2. Drag & drop resume files (PDF/DOC/DOCX)
3. Upload up to 50 resumes at once
4. System auto-processes and scores
5. Review results in bulk upload dashboard

**Processing Status:**
```
Uploaded: 50
Processed: 48 ✓
Failed: 2 ❌
Avg Processing Time: 12 seconds/resume
```

---

## Interview Scheduling

### Creating an Interview

**Navigate to:** `Interviews → Schedule New`

#### **Step 1: Select Candidate**
- Search by name or select from shortlist
- View candidate profile summary
- Check availability (if provided)

#### **Step 2: Interview Details**

| Field | Options |
|-------|---------|
| **Interview Type** | Phone, Video Call, In-Person |
| **Position** | Auto-filled from application |
| **Date** | Calendar picker |
| **Time** | Time slots (30/60/90 min) |
| **Duration** | 30, 45, 60, 90 minutes |
| **Location/Link** | Office address or video link |

#### **Step 3: Assign Interviewers**
```
Primary Interviewer: John Smith (HR Manager)
Additional Interviewers:
  + Sarah Johnson (Tech Lead)
  + Mike Chen (Senior Developer)
```

#### **Step 4: Interview Agenda** (Optional)
```
1. Introduction (5 min)
2. Work experience review (15 min)
3. Technical questions (30 min)
4. Candidate questions (5 min)
5. Next steps (5 min)
```

#### **Step 5: Notifications**
- [x] Send calendar invite to candidate
- [x] Send calendar invite to interviewers
- [x] Send reminder 1 day before
- [x] Send reminder 1 hour before

#### **Step 6: Confirm**
- Review all details
- Click "Schedule Interview"
- Emails sent automatically

### Managing Interviews

**View All Interviews:** `Interviews → Calendar View`

**Calendar Features:**
- **Day/Week/Month** views
- Filter by interviewer
- Filter by status
- Color-coded by interview type

**Interview Actions:**

| Action | Description |
|--------|-------------|
| **Reschedule** | Change date/time |
| **Cancel** | Cancel interview |
| **Add Notes** | Pre-interview notes |
| **Join Video Call** | Start video interview |
| **Mark Complete** | After interview done |

### Post-Interview Evaluation

**After the interview:** `Interviews → [Interview] → Add Feedback`

**Evaluation Form:**

```
Candidate: John Doe
Position: Senior Python Developer
Date: October 15, 2025
Interviewer: Sarah Johnson (Tech Lead)

Rating (1-5): ⭐⭐⭐⭐⭐

Technical Skills:     ⭐⭐⭐⭐⭐ (5/5)
Communication:        ⭐⭐⭐⭐   (4/5)
Problem Solving:      ⭐⭐⭐⭐⭐ (5/5)
Cultural Fit:         ⭐⭐⭐⭐   (4/5)
Overall Impression:   ⭐⭐⭐⭐⭐ (5/5)

Strengths:
- Excellent technical knowledge
- Clear communicator
- Strong problem-solving skills
- Relevant experience

Areas of Concern:
- Salary expectations slightly high
- Notice period is 2 months

Recommendation: [x] Strong Yes  [ ] Yes  [ ] No  [ ] Strong No

Additional Comments:
Highly recommended candidate. Technical skills are excellent and
would be a great addition to the team. Suggest moving to offer stage.
```

**Team Feedback Summary:**
```
3 Interviewers:
  ✓ Sarah Johnson: Strong Yes
  ✓ Mike Chen: Yes
  ✓ John Smith: Strong Yes

Average Rating: 4.7/5
Consensus: Move to Offer Stage
```

---

## Team Management

### Managing Your Recruitment Team

**Navigate to:** `Team → Team Members`

### Adding Team Members

**Add New Team Member:** `Team → Add Member`

**Step 1: Basic Information**
```
Full Name: Sarah Johnson
Email: sarah.johnson@company.com
Role: Recruiter
Department: Human Resources
```

**Step 2: Set Permissions**

| Permission | Company Admin | Recruiter |
|------------|---------------|-----------|
| Create jobs | ✓ | ✓ |
| Edit all jobs | ✓ | Own jobs only |
| View candidates | ✓ | ✓ |
| Schedule interviews | ✓ | ✓ |
| Send offers | ✓ | ✗ |
| Manage team | ✓ | ✗ |
| View analytics | ✓ | Limited |
| Manage settings | ✓ | ✗ |

**Step 3: Send Invitation**
- [x] Send welcome email
- [x] Require password change on first login
- [ ] Grant immediate access (or require approval)

### Managing Existing Team Members

**Team Member List View:**

```
┌─────────────────────────────────────────────────────────────┐
│ Name             Role        Status   Last Login   Actions   │
├─────────────────────────────────────────────────────────────┤
│ Sarah Johnson   Recruiter    Active   2 hours ago  [Edit]    │
│ Mike Chen       Recruiter    Active   1 day ago    [Edit]    │
│ Lisa Wong       Recruiter    Inactive 30 days ago  [Edit]    │
└─────────────────────────────────────────────────────────────┘
```

**Actions:**
- **Edit** - Update info and permissions
- **Deactivate** - Temporarily disable access
- **Remove** - Permanently remove from team
- **Reset Password** - Force password reset
- **View Activity** - See their actions log

### Activity Monitoring

**View Team Activity:** `Team → Activity Log`

**Track:**
- Jobs created/edited
- Candidates reviewed
- Interviews scheduled
- Notes added
- Status changes
- Login history

**Example Log:**
```
Today, 2:30 PM - Sarah Johnson shortlisted John Doe for Python Developer
Today, 1:15 PM - Mike Chen scheduled interview with Jane Smith
Today, 11:00 AM - Sarah Johnson created job posting: Marketing Manager
Yesterday, 4:45 PM - Mike Chen rejected 3 candidates
```

---

## Reports & Analytics

### Available Reports

**Navigate to:** `Reports → Analytics Dashboard`

### 1. Recruitment Overview Report

**Key Metrics:**
```
Current Month (October 2025)

Applications Received:        234
Candidates Shortlisted:        45
Interviews Conducted:          28
Offers Extended:                8
Hires Made:                     5
Rejection Rate:               78%
Offer Acceptance Rate:        63%
```

**Trend Chart:**
```
Applications per Month
│
│     ▄▄
│    ██
│   ███▄
│  ████
│ █████
│ █████
└─────────
 J F M A M J J A S O
```

### 2. Time-to-Hire Report

**Average Time by Stage:**
```
Application to Screening:     3 days
Screening to Interview:       7 days
Interview to Offer:          10 days
Offer to Acceptance:          5 days
─────────────────────────────────
Total Time-to-Hire:          25 days
```

**Comparison to Industry:**
```
Your Company:    25 days
Industry Avg:    35 days
Your Performance: 29% faster ✓
```

### 3. Source Effectiveness Report

**Where do your best candidates come from?**

```
Source          Apps   Hires   Conversion   Quality Score
───────────────────────────────────────────────────────────
LinkedIn         156      8       5.1%          8.2/10
Indeed            98      3       3.1%          7.5/10
Company Website   45      6      13.3%          9.1/10
Referral          28      5      17.9%          9.5/10
Job Boards        67      2       3.0%          6.8/10
```

**Recommendation:** Focus recruiting efforts on Company Website and Referrals

### 4. Diversity & Inclusion Report

**Gender Distribution:**
```
Applicants:  Male 55% | Female 43% | Other 2%
Shortlisted: Male 52% | Female 45% | Other 3%
Hired:       Male 50% | Female 48% | Other 2%
```

**Education Diversity:**
```
Bachelor's: 45%
Master's:   35%
PhD:        15%
Other:       5%
```

### 5. Interviewer Performance

**Interview feedback metrics:**

```
Interviewer      Interviews   Avg Rating   Feedback Quality
────────────────────────────────────────────────────────────
Sarah Johnson         45         4.2         Detailed
Mike Chen            38         4.5         Excellent
Lisa Wong            22         3.8         Good
```

### Exporting Reports

**Export Options:**
```
Reports → [Select Report] → Export
```

**Formats:**
- PDF (formatted report)
- Excel (XLSX with charts)
- CSV (raw data)
- PowerPoint (presentation)

**Schedule Automated Reports:**
```
Reports → Schedule → Set Frequency

Frequency: [ ] Daily  [x] Weekly  [ ] Monthly
Email to: john.smith@company.com
Format:   PDF
```

---

## Company Settings

### Configuring Company Profile

**Navigate to:** `Settings → Company Profile`

**Editable Fields:**
- Company Name
- Contact Information
- Address
- Website
- Logo
- Company Description
- Social Media Links

### Career Page Customization

**Settings → Career Page**

**Customize:**
- Header image/banner
- Company description
- Testimonials
- Office photos
- Company culture videos
- Benefits highlights

**Preview:** See live preview before publishing

**Custom Domain:** (If configured)
```
careers.yourcompany.com
```

### Email Templates

**Settings → Email Templates**

**Customize templates for:**
- Application received confirmation
- Interview invitation
- Interview reminder
- Rejection email
- Offer letter
- Welcome email

**Template Editor:**
```
Subject: Interview Invitation - [Position]

Dear [Candidate Name],

We are pleased to invite you for an interview for the
[Position] role at [Company Name].

Interview Details:
Date: [Date]
Time: [Time]
Duration: [Duration]
Location: [Location/Link]
Interviewers: [Interviewers]

Please confirm your availability by clicking the link below:
[Confirmation Link]

Best regards,
[Your Name]
[Company Name]
```

**Variables Available:**
```
[Candidate Name]
[Position]
[Company Name]
[Date]
[Time]
[Your Name]
[Custom Fields]
```

### Application Form Settings

**Settings → Application Form**

**Configure fields:**
- Required fields
- Optional fields
- Custom questions
- File upload requirements
- GDPR compliance checkbox

**Example Configuration:**
```
✓ Name (Required)
✓ Email (Required)
✓ Phone (Required)
✓ Resume Upload (Required)
✓ Cover Letter (Optional)
✓ LinkedIn Profile (Optional)

Custom Questions:
1. Why are you interested in this role?
2. What are your salary expectations?
3. When can you start?

✓ Enable GDPR consent checkbox
✓ Auto-delete applications after 180 days
```

---

## Best Practices

### 1. Job Posting Best Practices

✅ **Do:**
- Use clear, descriptive job titles
- Include salary ranges (increases applications by 30%)
- Highlight company culture and benefits
- Use inclusive language
- Keep descriptions concise (300-700 words)
- Include required vs. preferred skills
- Set realistic requirements
- Update postings regularly

❌ **Don't:**
- Use jargon or acronyms without explanation
- Create unrealistic requirements
- Copy/paste generic descriptions
- Forget to proofread
- Use discriminatory language

### 2. Candidate Screening Best Practices

✅ **Guidelines:**
- Review applications within 24-48 hours
- Use AI match scores as guidance, not absolute
- Look beyond keywords to actual experience
- Consider potential, not just qualifications
- Keep detailed notes for future reference
- Communicate rejections promptly and professionally
- Maintain talent pool for future opportunities

### 3. Interview Best Practices

✅ **Before Interview:**
- Review candidate's resume thoroughly
- Prepare specific questions
- Coordinate with interview panel
- Test video conferencing setup
- Send confirmation and reminders

✅ **During Interview:**
- Start on time
- Create welcoming environment
- Ask behavioral and situational questions
- Allow candidate to ask questions
- Take notes
- Explain next steps clearly

✅ **After Interview:**
- Submit feedback within 24 hours
- Compare notes with panel
- Communicate decision promptly
- Provide feedback if requested

### 4. Data Management

✅ **Best Practices:**
- Regularly archive old applications
- Maintain GDPR compliance
- Secure candidate data
- Don't share without permission
- Use secure communication channels
- Regular data backups

### 5. Team Collaboration

✅ **Effective Collaboration:**
- Use @mentions in notes
- Tag candidates appropriately
- Share interview feedback promptly
- Hold regular pipeline reviews
- Communicate hiring decisions quickly
- Document decision rationale

---

## Keyboard Shortcuts

Increase your productivity with these shortcuts:

| Shortcut | Action |
|----------|--------|
| **Ctrl + N** | New job posting |
| **Ctrl + F** | Search candidates |
| **Ctrl + K** | Quick command |
| **Ctrl + I** | Schedule interview |
| **Ctrl + R** | Open reports |
| **Ctrl + S** | Save current page |
| **Ctrl + /** | Help menu |
| **Esc** | Close modal |
| **Tab** | Navigate fields |
| **Enter** | Submit/Confirm |

---

## Troubleshooting

### Common Issues

**Issue: Candidate not receiving emails**
✓ Check spam/junk folder
✓ Verify email address correct
✓ Check email template settings
✓ Contact support if issue persists

**Issue: Can't upload resume**
✓ Check file size (<10MB)
✓ Use supported format (PDF, DOC, DOCX)
✓ Try different browser
✓ Clear browser cache

**Issue: Interview not appearing in calendar**
✓ Refresh page
✓ Check date/time zone settings
✓ Verify calendar sync enabled
✓ Check filter settings

---

## Getting Help

**Support Resources:**
- **Knowledge Base:** help.resumify.com
- **Video Tutorials:** resumify.com/tutorials
- **Email Support:** support@resumify.com
- **Live Chat:** Available in dashboard
- **Phone:** 1-800-RESUMIFY

**Support Hours:**
- Monday-Friday: 9 AM - 6 PM EST
- Response Time: Within 4 hours

---

**Need Help?** Contact your Company Admin or support@resumify.com

**© 2025 Resumify. All Rights Reserved.**
