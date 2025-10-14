# Resumify - Quick Reference Guide

**Version:** 1.0
**For:** All Users (Admin, HR Manager, Recruiter)

---

## 📖 Table of Contents

1. [User Roles Overview](#user-roles-overview)
2. [Common Tasks by Role](#common-tasks-by-role)
3. [Keyboard Shortcuts](#keyboard-shortcuts)
4. [Status Definitions](#status-definitions)
5. [Match Score Guide](#match-score-guide)
6. [Email Templates](#email-templates)
7. [Troubleshooting](#troubleshooting)
8. [Support Contacts](#support-contacts)

---

## User Roles Overview

### 🔵 Super Admin (System Owner)

**Access Level:** Full System Access

**Key Responsibilities:**
- ✅ Create and manage companies
- ✅ System-wide configuration
- ✅ Monitor system health
- ✅ Manage subscriptions
- ✅ Security administration

**Can Access:**
- All companies
- All users
- System settings
- Analytics & reports
- Security logs

**Cannot Be:** Part of any specific company

---

### 🟢 Company Admin (HR Manager)

**Access Level:** Full Company Access

**Key Responsibilities:**
- ✅ Post and manage jobs
- ✅ Review all candidates
- ✅ Manage recruitment team
- ✅ Schedule interviews
- ✅ Generate reports
- ✅ Configure company settings

**Can Access:**
- Own company's data
- All job postings
- All candidates
- Team members
- Company analytics

**Cannot Access:**
- Other companies
- System-wide settings
- Other companies' data

---

### 🟡 Recruiter

**Access Level:** Limited Company Access

**Key Responsibilities:**
- ✅ Review assigned candidates
- ✅ Screen applications
- ✅ Schedule interviews
- ✅ Communicate with candidates
- ✅ Update candidate status

**Can Access:**
- Assigned job postings
- Candidates for assigned jobs
- Own interview schedule
- Communication tools

**Cannot Access:**
- Company settings
- Team management
- Other recruiters' jobs
- Financial information

---

## Common Tasks by Role

### Super Admin Tasks

| Task | Navigation | Time |
|------|-----------|------|
| Create new company | Dashboard → Companies → Create | 5 min |
| View system health | Dashboard → Monitoring | 1 min |
| Reset user password | Users → [User] → Reset Password | 2 min |
| Review security logs | Security → Audit Logs | 5 min |
| Configure SMTP | Settings → Email → SMTP Config | 10 min |
| Manage subscriptions | Companies → [Company] → Subscription | 3 min |

---

### HR Manager / Company Admin Tasks

| Task | Navigation | Time |
|------|-----------|------|
| Post new job | Jobs → Create New Job | 15 min |
| Review candidates | Candidates → All Candidates | varies |
| Schedule interview | Candidates → [Candidate] → Schedule | 5 min |
| Add team member | Team → Add Member | 5 min |
| Generate report | Reports → Select Report → Export | 3 min |
| Update company profile | Settings → Company Profile | 10 min |
| Customize career page | Settings → Career Page | 20 min |

---

### Recruiter Tasks

| Task | Navigation | Time |
|------|-----------|------|
| Review application | My Jobs → [Job] → Applications | 10 min |
| Shortlist candidate | Candidates → [Candidate] → Shortlist | 1 min |
| Reject candidate | Candidates → [Candidate] → Reject | 2 min |
| Schedule interview | Candidates → [Candidate] → Schedule | 5 min |
| Send email | Candidates → [Candidate] → Send Message | 3 min |
| Add notes | Candidates → [Candidate] → Add Note | 2 min |
| Update status | Candidates → [Candidate] → Change Status | 1 min |

---

## Keyboard Shortcuts

### Universal Shortcuts (All Users)

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Quick search / Command palette |
| `Ctrl + F` | Find / Search |
| `Ctrl + S` | Save current page |
| `Ctrl + /` | Show help menu |
| `Esc` | Close modal / popup |
| `Tab` | Navigate between fields |
| `Enter` | Submit / Confirm |

### Role-Specific Shortcuts

**Super Admin:**
| Shortcut | Action |
|----------|--------|
| `Ctrl + Shift + C` | Create new company |
| `Ctrl + Shift + U` | User management |
| `Ctrl + Shift + S` | System settings |
| `Ctrl + Shift + M` | Monitoring dashboard |

**HR Manager:**
| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New job posting |
| `Ctrl + I` | Schedule interview |
| `Ctrl + R` | View reports |
| `Ctrl + T` | Team management |

**Recruiter:**
| Shortcut | Action |
|----------|--------|
| `S` | Shortlist candidate (in candidate view) |
| `R` | Reject candidate (in candidate view) |
| `N` | Add note |
| `E` | Send email |
| `I` | Schedule interview |
| `← →` | Previous / Next candidate |

---

## Status Definitions

### Candidate Status

| Status | Icon | Description | Who Can Set |
|--------|------|-------------|-------------|
| **New** | 🆕 | Just applied, not reviewed yet | System (automatic) |
| **Screening** | 🔍 | Being reviewed by recruiter | Recruiter, HR Manager |
| **Shortlisted** | ⭐ | Passed initial screening | Recruiter, HR Manager |
| **Interviewing** | 📅 | Interview scheduled or in progress | HR Manager, Recruiter |
| **Offer** | 💼 | Offer extended | HR Manager |
| **Hired** | ✅ | Accepted offer, starting soon | HR Manager |
| **Rejected** | ❌ | Not moving forward | Recruiter, HR Manager |
| **Withdrawn** | 🚪 | Candidate withdrew | HR Manager, Recruiter |
| **On Hold** | ⏸️ | Paused, may revisit later | HR Manager |

### Job Status

| Status | Description | Action Required |
|--------|-------------|-----------------|
| **Draft** | Not published yet | Complete and publish |
| **Active** | Live and accepting applications | Monitor applications |
| **Paused** | Temporarily not accepting | Resume or close |
| **Closed** | Position filled | Archive |
| **Expired** | Past deadline | Extend or close |

### Interview Status

| Status | Description | Next Action |
|--------|-------------|-------------|
| **Scheduled** | Confirmed and upcoming | Prepare and attend |
| **In Progress** | Currently happening | Complete |
| **Completed** | Finished, awaiting feedback | Submit feedback |
| **Cancelled** | Interview cancelled | Reschedule if needed |
| **No Show** | Candidate didn't attend | Follow up |

---

## Match Score Guide

### Understanding AI Match Scores

**How it's calculated:**

```
Match Score (0-100%) = Weighted Average of:
- Skills Match (40%)
- Experience Match (30%)
- Education Match (20%)
- Keywords & Others (10%)
```

### Score Interpretation

| Score Range | Badge | Interpretation | Action |
|-------------|-------|----------------|--------|
| **90-100%** | ⭐⭐⭐⭐⭐ | Excellent Match | Immediate shortlist & fast-track |
| **80-89%** | ⭐⭐⭐⭐ | Strong Match | Shortlist for interview |
| **70-79%** | ⭐⭐⭐ | Good Match | Review carefully, consider |
| **60-69%** | ⭐⭐ | Moderate Match | Review if few applicants |
| **Below 60%** | ⭐ | Weak Match | Usually reject unless special case |

### Score Components

**Skills Match (40% weight):**
```
Required Skills: 5 needed / 5 found = 100%
Preferred Skills: 3 needed / 2 found = 67%
Combined: (100% × 0.7) + (67% × 0.3) = 90%
```

**Experience Match (30% weight):**
```
Required: 5+ years
Candidate: 7 years
Score: 100% (exceeds minimum)
```

**Education Match (20% weight):**
```
Required: Bachelor's degree
Candidate: Bachelor's + certifications
Score: 100%
```

### Important Notes

⚠️ **Don't rely solely on match scores!**
- Review actual resume
- Consider intangibles (communication, culture fit)
- Check for transferable skills
- Look for growth potential

✅ **Best Practice:**
- Use scores to prioritize review order
- Read full profiles of 70%+ matches
- Give special consideration to 85%+ matches

---

## Email Templates

### Quick Copy-Paste Templates

#### **1. Application Received**
```
Subject: Application Received - [Position]

Dear [Candidate Name],

Thank you for applying for the [Position] role at [Company Name].

We have received your application and will review it within 3-5
business days. If your qualifications match our requirements,
we will contact you to schedule an interview.

Best regards,
[Your Name]
[Title]
[Company Name]
```

#### **2. Interview Invitation**
```
Subject: Interview Invitation - [Position]

Dear [Candidate Name],

We are pleased to invite you for an interview for the [Position]
role at [Company Name].

Interview Details:
Date: [Date]
Time: [Time] [Timezone]
Duration: [Duration] minutes
Type: [Phone/Video/In-Person]
Location/Link: [Details]

Please confirm your availability by replying to this email.

We look forward to speaking with you!

Best regards,
[Your Name]
```

#### **3. Interview Reminder**
```
Subject: Interview Reminder - Tomorrow at [Time]

Hi [Candidate Name],

This is a friendly reminder about your interview tomorrow:

Position: [Position]
Date: [Date]
Time: [Time] [Timezone]
Meeting Link: [Link]

Please join 5 minutes early to test your connection.

See you tomorrow!

Best regards,
[Your Name]
```

#### **4. Rejection (Respectful)**
```
Subject: Update on Your Application - [Position]

Dear [Candidate Name],

Thank you for your interest in the [Position] role at [Company Name]
and for taking the time to apply.

After careful review of all applications, we have decided to move
forward with other candidates whose qualifications more closely
align with the specific requirements of this role.

We appreciate your interest in [Company Name] and encourage you
to apply for future openings that match your background.

Best wishes in your job search.

Sincerely,
[Your Name]
[Title]
[Company Name]
```

#### **5. Offer Letter (Basic)**
```
Subject: Job Offer - [Position] at [Company Name]

Dear [Candidate Name],

We are delighted to extend an offer for the position of [Position]
at [Company Name].

Offer Details:
Position: [Position]
Start Date: [Date]
Salary: [Amount] per [year/hour]
Benefits: [List key benefits]

Please review the attached formal offer letter. We would love to
hear your decision by [Date].

Congratulations! We look forward to welcoming you to the team.

Best regards,
[Your Name]
[Title]
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Can't Login

**Solutions:**
1. Check caps lock is off
2. Verify correct username (not email)
3. Try "Forgot Password" link
4. Clear browser cache
5. Try incognito/private mode
6. Contact IT support

#### Issue: Not Receiving Emails

**Solutions:**
1. Check spam/junk folder
2. Add noreply@resumify.com to contacts
3. Verify email address in profile
4. Check email notification settings
5. Contact support

#### Issue: Can't Upload Resume

**Solutions:**
1. Check file size (<10MB)
2. Use PDF, DOC, or DOCX format
3. Try different browser
4. Disable browser extensions
5. Check internet connection
6. Contact support

#### Issue: Match Score Seems Wrong

**Understanding:**
- AI is a tool, not perfect
- Review actual resume
- Check if skills are misinterpreted
- Consider context and experience
- Use judgment over scores

#### Issue: Interview Link Not Working

**Solutions:**
1. Copy link to new browser tab
2. Check meeting platform (Zoom/Meet)
3. Verify you have platform installed
4. Test connection beforehand
5. Have backup phone number ready
6. Contact candidate immediately

#### Issue: Candidate Not Responding

**Actions:**
1. Wait 48 hours after first contact
2. Send follow-up email
3. Try alternative contact (phone)
4. Mark as "No Response" after 5 days
5. Move to next candidate

---

## Best Practices Cheat Sheet

### ✅ Do's

**For Everyone:**
- ✅ Respond promptly (within 24 hours)
- ✅ Keep detailed notes
- ✅ Treat candidates with respect
- ✅ Follow up as promised
- ✅ Maintain confidentiality
- ✅ Use professional communication
- ✅ Document all interactions

**For Screening:**
- ✅ Read full resume, not just summary
- ✅ Look for transferable skills
- ✅ Consider growth potential
- ✅ Check for culture fit indicators
- ✅ Verify work authorization

**For Interviews:**
- ✅ Prepare questions in advance
- ✅ Test technology beforehand
- ✅ Be punctual
- ✅ Take detailed notes
- ✅ Provide clear next steps
- ✅ Submit feedback promptly

### ❌ Don'ts

**For Everyone:**
- ❌ Ghost candidates
- ❌ Make hasty decisions
- ❌ Skip documentation
- ❌ Share confidential info
- ❌ Discriminate in any way
- ❌ Overpromise
- ❌ Ignore red flags

**For Screening:**
- ❌ Rely solely on AI scores
- ❌ Reject without reviewing
- ❌ Use vague rejection reasons
- ❌ Keep candidates waiting too long

**For Interviews:**
- ❌ Be unprepared
- ❌ Run overtime without notice
- ❌ Make illegal questions
- ❌ Multitask during interview
- ❌ Skip feedback submission

---

## Important Metrics to Track

### For Recruiters

**Daily:**
- Applications reviewed
- Candidates shortlisted
- Interviews scheduled
- Response time

**Weekly:**
- Shortlist rate (15-20% target)
- Interview-to-offer ratio
- Candidate satisfaction

**Monthly:**
- Time-to-hire
- Quality of hire
- Source effectiveness

### For HR Managers

**Weekly:**
- Pipeline health
- Team productivity
- Bottlenecks

**Monthly:**
- Cost per hire
- Time-to-fill
- Offer acceptance rate
- Diversity metrics

---

## Emergency Contacts

### Support Escalation

**Level 1 - Self Help:**
- Knowledge Base: help.resumify.com
- Video Tutorials: resumify.com/tutorials
- This guide

**Level 2 - In-App:**
- Live Chat (bottom right)
- Help button (? icon)
- Your manager

**Level 3 - Direct Support:**
- Email: support@resumify.com
- Response: Within 4 hours (business days)

**Level 4 - Urgent:**
- Phone: 1-800-RESUMIFY
- For system outages or critical issues
- Available: Mon-Fri, 9 AM - 6 PM EST

### What to Include in Support Request

```
1. Your name and role
2. Company name
3. Description of issue
4. Steps you've tried
5. Screenshots (if applicable)
6. Browser and OS version
7. Urgency level
```

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | October 2025 | Initial release |

---

## Quick Links

- 📘 [Super Admin Manual](USER_MANUAL_SUPER_ADMIN.md)
- 📗 [HR Manager Manual](USER_MANUAL_HR_MANAGER.md)
- 📙 [Recruiter Manual](USER_MANUAL_RECRUITER.md)
- 🌐 [Help Center](https://help.resumify.com)
- 📧 [Support Email](mailto:support@resumify.com)

---

**Need Help?** Contact support@resumify.com

**© 2025 Resumify. All Rights Reserved.**
