# 🔗 Automated Job Application System for LinkedIn Using RPA

## 📌 Project Overview

This project is an **Automated Job Application System** built using **Python and Selenium WebDriver** to auto-apply for jobs on **LinkedIn** based on a pre-defined configuration. The system performs login, job search, filter application, form filling, and submission tasks, significantly reducing the time and manual effort needed for job applications.

---

## 🎯 Objectives

- Automate the end-to-end process of job application on LinkedIn.
- Enable job filtering using keywords, location, and experience level.
- Simulate human-like interaction to avoid detection or CAPTCHA triggers.
- Improve application efficiency and minimize manual effort.

---

## ⚙️ Features

- 🔐 Auto Login using secure credentials.
- 🔍 Job Search based on keywords and location.
- ✅ Easy Apply filter for relevant job postings.
- 📄 Auto Resume Upload and Form Fill-up.
- 🔁 Page Navigation and Multi-page Job Parsing.
- 📊 Logs applied jobs and skips incomplete forms.

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Libraries**: 
  - `selenium`
  - `time`, `json`, `os`
  - `ActionChains`, `WebDriverWait`, `By`, etc.
- **Tools**:
  - Google Chrome
  - ChromeDriver
- **Platform**:
  - LinkedIn Web Portal

---

## 🗂️ Project Structure

```plaintext
├── main.py                # Main Python script
├── config.json            # Configuration file (user credentials and preferences)
├── README.md              # Project documentation
├── server.js              # To Run GUI Website
├── GUI_Linkedin.html      # GUI File
