"""
Email service for sending interview notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self, smtp_host: Optional[str] = None, smtp_port: Optional[int] = None,
                 smtp_user: Optional[str] = None, smtp_password: Optional[str] = None):
        """
        Initialize email service

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.enabled = all([smtp_host, smtp_port, smtp_user, smtp_password])

    def generate_interview_email(
        self,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        interview_datetime: datetime,
        interview_type: str,
        interviewer_name: Optional[str] = None,
        meeting_link: Optional[str] = None,
        location: Optional[str] = None
    ) -> dict:
        """
        Generate interview invitation email content

        Args:
            candidate_name: Name of the candidate
            candidate_email: Email of the candidate
            job_title: Job title/position
            interview_datetime: Scheduled interview datetime
            interview_type: Type of interview (video, phone, in-person)
            interviewer_name: Name of the interviewer
            meeting_link: Video meeting link (for video interviews)
            location: Physical location (for in-person interviews)

        Returns:
            Dictionary with email subject and body
        """
        # Format datetime
        formatted_datetime = interview_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        formatted_date = interview_datetime.strftime("%A, %B %d, %Y")
        formatted_time = interview_datetime.strftime("%I:%M %p")

        # Build email subject
        subject = f"Interview Invitation - {job_title} Position"

        # Build email body
        body = f"""Dear {candidate_name},

Thank you for your interest in joining our team. We are pleased to invite you to interview for the {job_title} position.

Based on your qualifications and experience, we believe you could be an excellent fit for this role. We would like to meet with you to discuss the position in more detail and learn more about your background and career goals.

INTERVIEW DETAILS
==================

Position: {job_title}
Date: {formatted_date}
Time: {formatted_time}
Format: {interview_type.replace('-', ' ').title()} Interview"""

        # Add type-specific details
        if interview_type == "video" and meeting_link:
            body += f"\nMeeting Link: {meeting_link}"
            body += "\n\nPlease ensure you have a stable internet connection and test your camera and microphone before the interview."
        elif interview_type == "in-person" and location:
            body += f"\nLocation: {location}"
            body += "\n\nPlease plan to arrive 10 minutes early. Bring a copy of your resume and a valid ID."
        elif interview_type == "phone":
            body += "\n\nWe will call you at the phone number provided in your application. Please ensure you're in a quiet environment for the call."

        if interviewer_name:
            body += f"\nInterviewer: {interviewer_name}"

        body += """

WHAT TO EXPECT
==============
The interview will last approximately 60 minutes. We'll discuss your experience, skills, and how they align with the role requirements. You'll also have the opportunity to ask questions about the position and our company.

PREPARATION
===========
• Review the job description and requirements
• Prepare examples of your relevant experience
• Research our company and culture
• Prepare thoughtful questions about the role

Please confirm your attendance by replying to this email at your earliest convenience. If you need to reschedule, please let us know as soon as possible so we can arrange an alternative time.

If you have any questions or require any accommodations, please don't hesitate to reach out.

We look forward to meeting you!

Best regards,
HR Team
"""

        return {
            "subject": subject,
            "body": body,
            "to": candidate_email,
            "to_name": candidate_name
        }

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = "HR Team",
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (defaults to smtp_user)
            from_name: Sender name
            reply_to: Reply-to email address

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service is not configured. Email not sent.")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{from_email or self.smtp_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Set Reply-To header if provided
            if reply_to:
                msg['Reply-To'] = reply_to

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            logger.error(f"SMTP Details - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            logger.error(f"Full error: {repr(e)}")
            return False

    def send_interview_invitation(
        self,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        interview_datetime: datetime,
        interview_type: str,
        interviewer_name: Optional[str] = None,
        interviewer_email: Optional[str] = None,
        meeting_link: Optional[str] = None,
        location: Optional[str] = None
    ) -> dict:
        """
        Generate and send interview invitation email

        Args:
            candidate_name: Name of the candidate
            candidate_email: Email of the candidate
            job_title: Job title/position
            interview_datetime: Scheduled interview datetime
            interview_type: Type of interview (video, phone, in-person)
            interviewer_name: Name of the interviewer
            interviewer_email: Email of the interviewer (for Reply-To)
            meeting_link: Video meeting link (for video interviews)
            location: Physical location (for in-person interviews)

        Returns:
            Dictionary with email content and send status
        """
        # Generate email content
        email_content = self.generate_interview_email(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            job_title=job_title,
            interview_datetime=interview_datetime,
            interview_type=interview_type,
            interviewer_name=interviewer_name,
            meeting_link=meeting_link,
            location=location
        )

        # Update email body to include interviewer contact info
        if interviewer_email:
            email_content["body"] = email_content["body"].replace(
                "Best regards,\nHR Team",
                f"Best regards,\n{interviewer_name or 'HR Team'}\n{interviewer_email}"
            )

        # Send email with interviewer's email as Reply-To
        sent = self.send_email(
            to_email=email_content["to"],
            subject=email_content["subject"],
            body=email_content["body"],
            from_name=interviewer_name or "HR Team",
            reply_to=interviewer_email
        )

        return {
            **email_content,
            "sent": sent,
            "enabled": self.enabled
        }

    def send_password_reset_otp(
        self,
        to_email: str,
        to_name: str,
        otp: str
    ) -> bool:
        """
        Send password reset OTP email

        Args:
            to_email: Recipient email address
            to_name: Recipient name
            otp: OTP code

        Returns:
            True if email was sent successfully, False otherwise
        """
        subject = "Password Reset Request - Resumify"
        body = f"""Dear {to_name},

We received a request to reset your password for your Resumify account.

Your password reset code is: {otp}

This code will expire in 10 minutes.

If you did not request a password reset, please ignore this email or contact our support team if you have concerns.

Best regards,
Resumify Security Team
"""

        # For development: print OTP to console if email service is not configured
        if not self.enabled:
            logger.warning(f"Email service not configured. OTP for {to_email}: {otp}")
            print(f"\n{'='*60}")
            print(f"🔐 PASSWORD RESET OTP (Email service not configured)")
            print(f"{'='*60}")
            print(f"Recipient: {to_name} ({to_email})")
            print(f"OTP Code: {otp}")
            print(f"Valid for: 10 minutes")
            print(f"{'='*60}\n")
            return True  # Return True so the flow continues

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            from_name="Resumify Security"
        )
