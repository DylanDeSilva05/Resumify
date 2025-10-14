import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../contexts/ToastContext';

function About() {
  const { showToast } = useToast();
  const [showDemoModal, setShowDemoModal] = useState(false);

  return (
    <div>
      {/* Public Header for About Page */}
      <header>
        <div className="header-content">
          <Link to="/login" className="logo">Resumify</Link>
          <nav>
            <ul className="nav-links">
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/about" className="active">About Us</Link></li>
            </ul>
          </nav>
        </div>
      </header>

      <section className="hero">
        <div className="container">
          <h1>About Resumify</h1>
          <p>Revolutionizing HR recruitment with intelligent automation and data-driven insights that transform how companies discover and hire top talent</p>
        </div>
      </section>

      <main className="container about-content">
        {/* Mission & Vision */}
        <section className="content-section">
          <div className="section-header animate-on-scroll">
            <h2>Our Purpose</h2>
            <p>We believe in making recruitment smarter, faster, and more effective for HR professionals worldwide</p>
          </div>

          <div className="mission-vision">
            <div className="mission-card animate-on-scroll animate-delay-1">
              <h3>Our Mission</h3>
              <p>To empower HR teams with cutting-edge AI technology that streamlines the recruitment process, eliminates bias, and helps find the perfect candidates for every role. We're committed to making hiring decisions more objective, efficient, and successful through intelligent automation.</p>
            </div>
            <div className="vision-card animate-on-scroll animate-delay-2">
              <h3>Our Vision</h3>
              <p>To become the global leader in AI-powered recruitment solutions, transforming how companies discover, evaluate, and hire talent. We envision a future where every hiring decision is backed by intelligent insights and data-driven precision.</p>
            </div>
          </div>
        </section>

        {/* Services */}
        <section className="content-section">
          <div className="section-header animate-on-scroll">
            <h2>Our Services</h2>
            <p>Comprehensive recruitment solutions designed for modern HR teams</p>
          </div>

          <div className="services-grid">
            <div className="service-card animate-on-scroll animate-delay-1">
              <div className="service-icon">AI</div>
              <h3>AI-Powered Matching</h3>
              <p>Advanced algorithms analyze CVs and match candidates to job requirements with precision scoring and compatibility analysis</p>
            </div>
            <div className="service-card animate-on-scroll animate-delay-2">
              <div className="service-icon">⚡</div>
              <h3>Automated Screening</h3>
              <p>Intelligent candidate sorting into shortlisted and rejected categories based on customizable job criteria and requirements</p>
            </div>
            <div className="service-card animate-on-scroll animate-delay-3">
              <div className="service-icon">📅</div>
              <h3>Interview Management</h3>
              <p>Seamless scheduling and calendar integration for managing interview appointments with automated email notifications</p>
            </div>
            <div className="service-card animate-on-scroll animate-delay-1">
              <div className="service-icon">👥</div>
              <h3>Team Collaboration</h3>
              <p>Multi-user access with role-based permissions for HR team collaboration and streamlined workflow management</p>
            </div>
            <div className="service-card animate-on-scroll animate-delay-2">
              <div className="service-icon">📧</div>
              <h3>Email Automation</h3>
              <p>Customizable email templates for candidate communication, interview invitations, and recruitment follow-ups</p>
            </div>
            <div className="service-card animate-on-scroll animate-delay-3">
              <div className="service-icon">🔒</div>
              <h3>Enterprise Security</h3>
              <p>Enterprise-grade security with encrypted data storage, GDPR compliance, and comprehensive access controls</p>
            </div>
          </div>
        </section>

        {/* Key Features */}
        <section className="features-section animate-on-scroll">
          <div className="section-header">
            <h2>Why Choose Resumify?</h2>
            <p>Features that make the difference in modern recruitment</p>
          </div>

          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">⚡</div>
              <div className="feature-content">
                <h4>80% Time Reduction</h4>
                <p>Dramatically reduce screening time with automated candidate matching and intelligent processing</p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🎯</div>
              <div className="feature-content">
                <h4>Enhanced Accuracy</h4>
                <p>AI-powered algorithms ensure superior candidate-role compatibility with detailed skill assessment</p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📈</div>
              <div className="feature-content">
                <h4>Better Matches</h4>
                <p>Advanced scoring system analyzes thousands of data points to find the most suitable candidates</p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">⚖️</div>
              <div className="feature-content">
                <h4>Objective Hiring</h4>
                <p>Remove unconscious bias with data-driven candidate evaluation based on skills and experience</p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <div className="feature-content">
                <h4>Analytics & Insights</h4>
                <p>Comprehensive reporting and analytics to optimize your hiring process and track performance</p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">🔄</div>
              <div className="feature-content">
                <h4>Seamless Integration</h4>
                <p>Integrate with existing HR tools and systems for a unified, streamlined recruitment workflow</p>
              </div>
            </div>
          </div>
        </section>

        {/* Team */}
        <section className="team-section animate-on-scroll">
          <div className="section-header">
            <h2>Meet Our Team</h2>
            <p>The passionate professionals behind Resumify's innovation</p>
          </div>

          <div className="team-grid">
            <div className="team-member">
              {/* Replace with: <img src="/images/team/supuni.jpg" alt="Supuni Weligalla" className="member-photo" /> */}
              <div className="member-avatar">SW</div>
              <div className="member-name">Supuni Weligalla</div>
              <div className="member-role">Frontend Developer</div>
              <div className="member-bio">Passionate about creating intuitive user experiences. Specializes in React, modern CSS, and responsive design. Turned complex recruitment workflows into elegant interfaces.</div>
            </div>
            <div className="team-member">
              {/* Replace with: <img src="/images/team/nimmi.jpg" alt="Nimmi Abeykoon" className="member-photo" /> */}
              <div className="member-avatar">NA</div>
              <div className="member-name">Nimmi Abeykoon</div>
              <div className="member-role">Database Architect</div>
              <div className="member-bio">Database expert specializing in PostgreSQL and data modeling. Designed scalable database architectures that handle thousands of candidate records efficiently.</div>
            </div>
            <div className="team-member">
              {/* Replace with: <img src="/images/team/miuri.jpg" alt="Miuri Abeykoon" className="member-photo" /> */}
              <div className="member-avatar">MA</div>
              <div className="member-name">Miuri Abeykoon</div>
              <div className="member-role">Backend Developer</div>
              <div className="member-bio">Backend architect focused on building scalable FastAPI systems. Implemented AI-powered CV parsing and candidate matching algorithms.</div>
            </div>
            <div className="team-member">
              {/* Replace with: <img src="/images/team/dewshini.jpg" alt="Dewshini Mendis" className="member-photo" /> */}
              <div className="member-avatar">DM</div>
              <div className="member-name">Dewshini Mendis</div>
              <div className="member-role">Security Engineer</div>
              <div className="member-bio">Cybersecurity specialist ensuring enterprise-grade protection. Implemented multi-factor authentication, encryption, and GDPR compliance.</div>
            </div>
            <div className="team-member">
              {/* Replace with: <img src="/images/team/dylan.jpg" alt="Dylan De Silva" className="member-photo" /> */}
              <div className="member-avatar">DD</div>
              <div className="member-name">Dylan De Silva</div>
              <div className="member-role">Full Stack Developer</div>
              <div className="member-bio">Full-stack engineer bridging frontend and backend. Integrated email systems, calendar management, and real-time notifications.</div>
            </div>
          </div>
        </section>

        {/* Contact */}
        <section className="contact-section animate-on-scroll">
          <div className="container">
            <h2>Ready to Transform Your Hiring Process?</h2>
            <p>Get in touch with our team to learn how Resumify can revolutionize your recruitment workflow and help you find the perfect candidates faster</p>

            <div className="contact-info">
              <div className="contact-item">
                <h3>Sales Inquiries</h3>
                <p>sales@resumify.com</p>
                <p>Get a personalized demo and pricing</p>
              </div>
              <div className="contact-item">
                <h3>Customer Support</h3>
                <p>support@resumify.com</p>
                <p>24/7 technical assistance available</p>
              </div>
              <div className="contact-item">
                <h3>Phone Support</h3>
                <p>+1 (555) 123-4567</p>
                <p>Monday-Friday 9AM-6PM EST</p>
              </div>
            </div>

            <button className="cta-button" onClick={() => setShowDemoModal(true)}>View Demo Video</button>
          </div>
        </section>
      </main>

      {/* Demo Video Modal */}
      {showDemoModal && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowDemoModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px' }}>
            <div className="modal-header">
              <h2>🎥 Resumify Platform Demo</h2>
              <span className="close" onClick={() => setShowDemoModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', background: '#000', borderRadius: '8px' }}>
                <iframe
                  src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  title="Resumify Demo Video"
                />
              </div>
              <p style={{ marginTop: '1.5rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                📌 See how Resumify transforms your recruitment process in just 2 minutes
              </p>
              <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center' }}>
                Note: Replace the YouTube video ID in the code with your actual demo video
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default About;