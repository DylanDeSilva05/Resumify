# Resumify - Super Administrator User Manual

**Version:** 1.0
**Last Updated:** October 2025
**Role:** Super Administrator (System Owner)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Company Management](#company-management)
5. [System Configuration](#system-configuration)
6. [User Management](#user-management)
7. [Monitoring & Analytics](#monitoring-analytics)
8. [Security Settings](#security-settings)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Introduction

### What is a Super Administrator?

As a **Super Administrator**, you have the highest level of access in Resumify. You are responsible for:

✅ Creating and managing multiple companies
✅ System-wide configuration and settings
✅ Monitoring system health and performance
✅ Managing subscription tiers
✅ Troubleshooting across all organizations

**Note:** Super Admins do not belong to any specific company and can oversee the entire platform.

---

## Getting Started

### First-Time Login

1. **Access the System**
   - Navigate to: `https://your-resumify-domain.com/admin`
   - Enter your Super Admin credentials
   - You'll be prompted to enable Two-Factor Authentication (2FA) - **Highly Recommended**

2. **Enable Two-Factor Authentication**
   ```
   Profile → Security Settings → Enable 2FA
   ```
   - Scan QR code with Google Authenticator or Authy
   - Save backup codes in a secure location
   - Enter 6-digit code to verify

3. **Initial Setup Checklist**
   - [ ] Enable 2FA
   - [ ] Review system settings
   - [ ] Create first company
   - [ ] Configure SMTP settings
   - [ ] Set up backup schedule

---

## Dashboard Overview

### Main Dashboard Components

**1. System Health Panel**
- Server status (CPU, Memory, Disk usage)
- Database connection status
- Active users count
- API response times

**2. Quick Statistics**
- Total Companies: X
- Total Users: X
- Active Subscriptions: X
- Storage Used: X GB / Total GB

**3. Recent Activity Feed**
- New company registrations
- User login activity
- System errors/warnings
- Subscription changes

**4. Quick Actions**
- Create New Company
- View System Logs
- Manage Subscriptions
- Security Audit

---

## Company Management

### Creating a New Company

**Step 1: Navigate to Companies**
```
Dashboard → Companies → Create New Company
```

**Step 2: Fill in Company Details**

| Field | Description | Required |
|-------|-------------|----------|
| Company Name | Legal business name | Yes |
| Contact Email | Primary contact email | Yes |
| Contact Phone | Business phone number | Optional |
| Address | Full business address | Optional |
| Industry | Company industry sector | Optional |
| Website | Company website URL | Optional |

**Step 3: Configure Subscription**

Choose subscription tier:

| Tier | Max Users | Monthly CV Uploads | Price |
|------|-----------|-------------------|-------|
| Basic | 5 | 100 | $49/month |
| Premium | 20 | 500 | $149/month |
| Enterprise | Unlimited | Unlimited | $499/month |

**Step 4: Create Company Admin**
- Username: company_admin
- Email: admin@company.com
- Password: (Auto-generate secure password)
- Role: Company Admin
- Send welcome email: ✓

**Step 5: Review and Confirm**
- Review all information
- Click "Create Company"
- Company admin receives email with login credentials

### Managing Existing Companies

**View All Companies**
```
Dashboard → Companies → View All
```

**Company Actions:**
- **Edit** - Update company information
- **Suspend** - Temporarily disable company access
- **Activate** - Re-enable suspended company
- **Delete** - Permanently remove company (requires confirmation)
- **View Details** - See full company profile

**Company Details View:**
- Company Information
- Subscription Details
- Usage Statistics
- User List
- Recent Activity
- Billing History

### Subscription Management

**Upgrade/Downgrade Subscription**
1. Go to: `Companies → [Company Name] → Subscription`
2. Select new tier
3. Confirm changes
4. System automatically adjusts limits

**View Usage Metrics**
- Current users vs. max users
- CV uploads this month vs. limit
- Storage usage
- API calls (if applicable)

**Billing Actions**
- View invoice history
- Download invoices (PDF)
- Update payment method
- Apply promotional codes

---

## System Configuration

### Global Settings

**Navigate to:** `Settings → System Configuration`

#### 1. General Settings

```yaml
System Settings:
  - Platform Name: Resumify
  - Support Email: support@resumify.com
  - Timezone: UTC
  - Date Format: MM/DD/YYYY
  - Currency: USD
```

#### 2. Email Configuration (SMTP)

**Setup Instructions:**

1. Click "Email Settings"
2. Fill in SMTP details:

| Setting | Example Value |
|---------|---------------|
| SMTP Host | smtp.gmail.com |
| SMTP Port | 587 |
| SMTP Username | noreply@resumify.com |
| SMTP Password | [App Password] |
| From Name | Resumify Notifications |
| Use TLS | ✓ Enabled |

3. Click "Test Email" to verify
4. Save configuration

**Common SMTP Providers:**
- **Gmail:** smtp.gmail.com:587
- **SendGrid:** smtp.sendgrid.net:587
- **Amazon SES:** email-smtp.us-east-1.amazonaws.com:587

#### 3. Security Settings

**Password Policy:**
```
✓ Minimum 8 characters
✓ Require uppercase letter
✓ Require lowercase letter
✓ Require number
✓ Require special character
✓ Password expiry: 90 days (optional)
```

**Session Management:**
- Session timeout: 15 minutes (idle)
- Max concurrent sessions: 3
- Force logout on password change: ✓

**Rate Limiting:**
- Max login attempts: 5
- Lockout duration: 30 minutes
- API rate limit: 1000 requests/hour

#### 4. File Upload Settings

```yaml
Upload Configuration:
  - Max file size: 10 MB
  - Allowed formats: PDF, DOC, DOCX
  - Storage location: AWS S3 / Local
  - Virus scanning: Enabled
  - Auto-delete after: 365 days (optional)
```

#### 5. AI/ML Settings

**Resume Analysis Configuration:**
- Enable AI parsing: ✓
- Skills extraction: Enabled
- Experience calculation: Enabled
- Education parsing: Enabled
- Language detection: Enabled

**Matching Algorithm:**
- Minimum match score: 70%
- Weight factors:
  - Skills match: 40%
  - Experience: 30%
  - Education: 20%
  - Keywords: 10%

---

## User Management

### Managing System Users

**View All Users Across All Companies:**
```
Dashboard → Users → All Users
```

**Filters:**
- By Company
- By Role
- By Status (Active/Inactive)
- By Last Login

### User Actions

**Impersonate User (Troubleshooting)**
1. Go to: `Users → [User Name] → Actions`
2. Click "Impersonate"
3. View system as that user
4. Click "Exit Impersonation" when done

**⚠️ Warning:** All actions taken during impersonation are logged.

**Reset User Password**
1. Select user
2. Click "Reset Password"
3. Choose:
   - Auto-generate and email
   - Set temporary password
4. User must change on next login

**Disable/Enable User**
- **Disable:** User cannot login but data is preserved
- **Enable:** Restore user access

**Audit User Activity**
```
Users → [User Name] → Activity Log
```
View:
- Login history
- Actions performed
- Files uploaded/downloaded
- API calls made

---

## Monitoring & Analytics

### System Monitoring Dashboard

**Real-Time Metrics:**
```
Dashboard → Monitoring → System Health
```

**Key Metrics:**
1. **Server Performance**
   - CPU Usage: 45%
   - Memory Usage: 3.2 GB / 8 GB
   - Disk Usage: 120 GB / 500 GB
   - Network I/O: 50 MB/s

2. **Database Performance**
   - Active connections: 25 / 100
   - Query response time: 45ms avg
   - Slow queries: 3
   - Database size: 2.5 GB

3. **Application Metrics**
   - Active users: 234
   - API requests/min: 450
   - Error rate: 0.02%
   - Avg response time: 120ms

### Analytics & Reports

**Usage Analytics:**
```
Dashboard → Analytics → Usage Reports
```

**Available Reports:**

1. **Company Activity Report**
   - Companies created
   - Active vs inactive companies
   - Subscription distribution
   - Revenue by tier

2. **User Activity Report**
   - Daily active users
   - User growth trend
   - Login frequency
   - Feature usage

3. **Resume Processing Report**
   - CVs uploaded per day
   - Processing success rate
   - Average processing time
   - Storage growth

4. **System Performance Report**
   - Uptime percentage
   - Average response time
   - Error rate trend
   - API usage

**Export Reports:**
- PDF
- Excel (XLSX)
- CSV
- JSON

---

## Security Settings

### Security Audit Log

**Access Audit Logs:**
```
Dashboard → Security → Audit Logs
```

**Logged Events:**
- User logins (success/failure)
- Password changes
- Permission changes
- Data exports
- Configuration changes
- File uploads/downloads
- API access

**Filter Logs:**
- By date range
- By user
- By company
- By event type
- By severity (Info, Warning, Error, Critical)

### IP Whitelisting

**Configure IP Restrictions:**
```
Settings → Security → IP Whitelist
```

1. Click "Add IP Range"
2. Enter IP address or CIDR range
3. Add description
4. Enable/Disable
5. Save

**Example:**
```
Office Network: 203.0.113.0/24
VPN Gateway: 198.51.100.50
```

### Two-Factor Authentication Management

**Enforce 2FA Globally:**
```
Settings → Security → Two-Factor Authentication
```

Options:
- [ ] Optional (users can enable)
- [x] Required for admins
- [ ] Required for all users
- Grace period: 7 days

### Security Alerts

**Configure Alerts:**
```
Settings → Security → Alert Rules
```

**Alert Types:**
- Multiple failed login attempts
- Unusual access patterns
- Large data exports
- Configuration changes
- System errors
- Storage threshold exceeded

**Notification Methods:**
- Email
- SMS (if configured)
- Slack webhook
- System dashboard

---

## Troubleshooting

### Common Issues

#### Issue 1: User Cannot Login

**Symptoms:** User reports "Invalid credentials" error

**Resolution Steps:**
1. Verify user account is active
   ```
   Users → Search → Check "Is Active" status
   ```

2. Check if account is locked
   ```
   Users → [User] → Security → Check "Account Locked Until"
   ```

3. Reset password
   ```
   Users → [User] → Reset Password → Send Email
   ```

4. Verify email address is correct

5. Check company subscription status

#### Issue 2: Email Not Sending

**Symptoms:** Users not receiving emails

**Resolution Steps:**
1. Test SMTP configuration
   ```
   Settings → Email → Test Email
   ```

2. Check SMTP credentials are correct

3. Verify firewall allows port 587

4. Check email logs
   ```
   Dashboard → Logs → Email Logs
   ```

5. Verify "From" email is not blacklisted

#### Issue 3: Slow System Performance

**Symptoms:** Pages loading slowly

**Resolution Steps:**
1. Check server resources
   ```
   Dashboard → Monitoring → System Health
   ```

2. Review slow database queries
   ```
   Monitoring → Database → Slow Queries
   ```

3. Check error logs
   ```
   Dashboard → Logs → Error Logs
   ```

4. Clear cache
   ```
   Settings → Advanced → Clear Cache
   ```

5. Restart application services (if needed)

#### Issue 4: Resume Upload Failing

**Symptoms:** "File upload failed" error

**Resolution Steps:**
1. Check file size limit
   ```
   Settings → File Upload → Max File Size
   ```

2. Verify storage quota not exceeded

3. Check file format is allowed

4. Review upload logs

5. Test upload with known good file

---

## Best Practices

### 1. Security Best Practices

✅ **Do:**
- Enable 2FA for all admin accounts
- Regularly review user access
- Monitor audit logs weekly
- Keep system updated
- Use strong, unique passwords
- Implement IP whitelisting for admin access
- Regular security audits
- Backup data regularly

❌ **Don't:**
- Share admin credentials
- Disable security features
- Ignore security alerts
- Use default passwords
- Grant unnecessary permissions
- Skip software updates

### 2. Company Management Best Practices

✅ **Guidelines:**
- Verify company information before activation
- Set appropriate subscription limits
- Document company-specific configurations
- Maintain communication with company admins
- Monitor usage patterns
- Plan for capacity growth
- Regular billing reviews

### 3. Data Management

✅ **Best Practices:**
- Schedule regular backups (daily recommended)
- Test restore procedures monthly
- Archive old data according to policy
- Monitor storage usage
- Implement data retention policies
- Ensure GDPR/compliance requirements met
- Document data handling procedures

### 4. Monitoring & Maintenance

**Daily Tasks:**
- [ ] Check system health dashboard
- [ ] Review error logs
- [ ] Monitor active users
- [ ] Verify backup completion

**Weekly Tasks:**
- [ ] Review security audit logs
- [ ] Check storage usage trends
- [ ] Analyze performance metrics
- [ ] Review user feedback/support tickets

**Monthly Tasks:**
- [ ] Generate usage reports
- [ ] Review and update security policies
- [ ] Audit user permissions
- [ ] Plan capacity/scaling needs
- [ ] Review and renew SSL certificates

**Quarterly Tasks:**
- [ ] Comprehensive security audit
- [ ] Disaster recovery drill
- [ ] Performance optimization review
- [ ] User training updates

---

## Emergency Procedures

### System Outage

**Immediate Actions:**
1. Check system status dashboard
2. Review error logs
3. Notify stakeholders
4. Post status update
5. Contact technical support if needed

**Communication Template:**
```
Subject: [URGENT] System Maintenance - Resumify

We are currently experiencing technical difficulties with Resumify.

Status: Under Investigation
Impact: Full system unavailable
ETA: Updates every 30 minutes

We apologize for the inconvenience and are working to resolve this ASAP.

- Resumify Support Team
```

### Data Breach Response

**If you suspect a security breach:**

1. **Immediately:**
   - Document the incident
   - Isolate affected systems
   - Preserve evidence

2. **Contact:**
   - Technical support team
   - Legal counsel
   - Affected companies

3. **Follow:**
   - Company incident response plan
   - Legal/regulatory requirements
   - Communication protocols

---

## Support & Resources

### Getting Help

**Technical Support:**
- Email: support@resumify.com
- Phone: 1-800-RESUMIFY
- Live Chat: Available in dashboard
- Priority: Super Admin requests handled within 1 hour

**Documentation:**
- User Manual: `/docs/user-manual`
- API Documentation: `/docs/api`
- Video Tutorials: `/docs/videos`
- Knowledge Base: `help.resumify.com`

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + K | Search |
| Ctrl + D | Dashboard |
| Ctrl + U | Users |
| Ctrl + C | Companies |
| Ctrl + S | Settings |
| Esc | Close modal |

---

## Appendix

### Glossary

- **Super Admin:** System owner with full access
- **Company Admin:** Manages individual company
- **Subscription Tier:** Service level and limits
- **2FA:** Two-Factor Authentication
- **SMTP:** Email server protocol
- **API:** Application Programming Interface
- **CV:** Curriculum Vitae (Resume)

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 2025 | Initial release |

---

**Need Help?** Contact support@resumify.com

**© 2025 Resumify. All Rights Reserved.**
