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

<<<<<<< HEAD
6. Run the application ( app.py )
=======
6. Run the app ( app.py )
>>>>>>> 77cc84d (Update README.md)
  
8. ![image](https://github.com/user-attachments/assets/6f64ca77-4874-42e4-b0c0-25baa62f93df)


📌 How to Use
-------------

1. Upload Calendar: Go to `/upload-calendar` and upload your academic calendar.
2. Map Lectures: Visit `/map-lecture` to assign subjects to weekdays.
3. Mark Attendance: Head to `/attendance`, click a date, and mark Present/Absent for each subject.
4. Check Summary: `/attendance-summary` gives a live subject-wise attendance breakdown.
5. Plan Vacation: Use `/vacation-planner` to generate valid vacation slots based on your attendance & threshold.

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
