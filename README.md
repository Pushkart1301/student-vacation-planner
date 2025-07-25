![MIT License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Flask](https://img.shields.io/badge/backend-Flask-orange)
====================================
🎒 Student Vacation Planner (SVP)
================================

Plan smarter vacations without risking your attendance!

The Student Vacation Planner helps students make informed vacation decisions by analyzing their academic calendar, subject-wise attendance, and lecture schedules. With just a few clicks, SVP tells you when it's safe to take a break — without falling below the required attendance percentage (e.g., 75%).

🚀 Features
-----------

- 📅 Upload your academic calendar (PDF/image)
- 🧠 OCR + AI to auto-detect holidays
- 🗓️ Map your weekly lecture schedule
- ✅ Mark subject-wise attendance daily (P/A)
- 📊 View subject-wise attendance summary
- 🌴 Get smart vacation suggestions based on your current attendance and threshold

🛠️ Getting Started
-------------------

1. Clone the repository

2. Set up your environment(recomended)
   cd student-vacation-planner
   python -m venv venv
   
3. Activate the virtual environment
   Windows (CMD): venv\Scripts\activate
   powershell: .\venv\Scripts\Activate.ps1
   macOS/Linux: source venv/bin/activate

5. Install project dependencies:
   pip install -r requirements.txt

7. Configure your API key

- Copy `.env.example` to `.env`
- Add your Groq API key inside `.env`:
GROQ_API_KEY=your_api_key_here

6. Run the application ( app.py )
=======
6. Run the app ( app.py )

  
8. ![image](https://github.com/user-attachments/assets/6f64ca77-4874-42e4-b0c0-25baa62f93df)


📌 How to Use
-------------

1. Upload Calendar: Go to `/upload-calendar` and upload your academic calendar.
2. Map Lectures: Visit `/map-lecture` to assign subjects to weekdays.
3. Mark Attendance: Head to `/attendance`, click a date, and mark Present/Absent for each subject.
4. Check Summary: `/attendance-summary` gives a live subject-wise attendance breakdown.
5. Plan Vacation: Use `/vacation-planner` to generate valid vacation slots based on your attendance & threshold.


![Black White Professional Minimal Brand Logo_page-0001](https://github.com/user-attachments/assets/8dca6501-db10-4eb6-808b-7e819c6c2038)
![Black White Professional Minimal Brand Logo_page-0002](https://github.com/user-attachments/assets/db3fb98c-2af2-458c-ae08-ea21e0bd18a7)
![Black White Professional Minimal Brand Logo_page-0003](https://github.com/user-attachments/assets/56655583-d3ef-4480-b9e0-3503f39a2924)




🤖 Tech Stack
-------------

- Flask for backend API
- Tailwind CSS + HTML for UI
- Pytesseract / PDFMiner for OCR & text parsing
- Groq API (LLaMA-3) for intelligent holiday extraction

📢 Contributing
---------------

Pull requests are welcome! If you'd like to improve features or fix bugs, feel free to fork and submit a PR.

📃 License
----------

This project is open-source under the MIT License.

💡 Pro Tip
----------

Keep your attendance updated daily for the most accurate vacation planning results!

⚠️ Note: I've already included a working API key in the project just for your ease of testing SVP. If you have your own Groq API key, you can replace it in the groq_module.py file or update the .env file accordingly.
