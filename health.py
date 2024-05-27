import streamlit as st
import pandas as pd
import sqlite3

# Create or connect to a SQLite database
conn = sqlite3.connect('hospital.db', check_same_thread=False)  # Added for Streamlit compatibility
c = conn.cursor()

# Create tables in the database if they don't already exist
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS Patients (
                    PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Age INTEGER NOT NULL,
                    Gender TEXT NOT NULL,
                    Address TEXT,
                    Phone TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Doctors (
                    DoctorID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Specialty TEXT NOT NULL
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Calories (
                    EntryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    DoctorID INTEGER,
                    TotalCalories INTEGER NOT NULL,
                    Date TEXT NOT NULL,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Symptoms (
                    SymptomID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    Symptoms TEXT NOT NULL,
                    Duration TEXT NOT NULL,
                    Allergy TEXT NOT NULL,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Diagnosis (
                    DiagnosisID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    Result TEXT NOT NULL,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS PhysicalFitness (
                    FitnessID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    TypeOfExercise TEXT,
                    Duration TEXT,
                    Benefit TEXT,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Prescription (
                    PrescriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    DoctorID INTEGER,
                    MedicineName TEXT,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Dispensary (
                    DispensaryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PatientID INTEGER,
                    DoctorID INTEGER,
                    PrescriptionID INTEGER,
                    Medicine TEXT,
                    Quantity INTEGER,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
                    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
                    FOREIGN KEY (PrescriptionID) REFERENCES Prescription(PrescriptionID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS Billing (
                    BillNo INTEGER PRIMARY KEY AUTOINCREMENT,
                    ModeOfPayment TEXT NOT NULL,
                    PatientID INTEGER,
                    ReceiptNo TEXT NOT NULL,
                    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS LabTests (
                    TestID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TypeOfTest TEXT NOT NULL,
                    DateOfTest TEXT NOT NULL
                )''')
    conn.commit()

create_tables()

# Additional functions for handling the database have been added below.
# Please add these functions into the Streamlit interface by following
# the same patterns as the existing add/view functions.
# Function to handle user input for adding a patient
def add_patient():
    st.subheader("Add New Patient")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=150, value=0)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    address = st.text_area("Address")
    phone = st.text_input("Phone")
    if st.button("Add Patient"):
        c.execute("INSERT INTO Patients (Name, Age, Gender, Address, Phone) VALUES (?, ?, ?, ?, ?)", 
                  (name, age, gender, address, phone))
        conn.commit()
        st.success("Patient added successfully!")

# Function to view patient records
def view_patients():
    st.subheader("Patient Records")
    patients = c.execute("SELECT * FROM Patients").fetchall()
    df_patients = pd.DataFrame(patients, columns=["PatientID", "Name", "Age", "Gender", "Address", "Phone"])
    st.dataframe(df_patients)

# Function to handle user input for adding a doctor
def add_doctor():
    st.subheader("Add New Doctor")
    name = st.text_input("Doctor's Name")
    specialty = st.text_input("Specialty")
    if st.button("Add Doctor"):
        c.execute("INSERT INTO Doctors (Name, Specialty) VALUES (?, ?)", (name, specialty))
        conn.commit()
        st.success("Doctor added successfully!")

# Function to view doctor records
def view_doctors():
    st.subheader("Doctor Records")
    doctors = c.execute("SELECT * FROM Doctors").fetchall()
    df_doctors = pd.DataFrame(doctors, columns=["DoctorID", "Name", "Specialty"])
    st.dataframe(df_doctors)

# Function to handle user input for scheduling an appointment


# Function to add a healthy diet plan
def add_healthy_diet():
    st.subheader("Add Healthy Diet Plan")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    doctor_data = c.execute("SELECT DoctorID, Name FROM Doctors").fetchall()

    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}
    doctor_options = {f"{did}: {name}": did for did, name in doctor_data}

    selected_patient = st.selectbox("Select Patient for Diet", options=list(patient_options.keys()))
    selected_doctor = st.selectbox("Select Doctor for Diet", options=list(doctor_options.keys()))
    diet_description = st.text_area("Diet Description")

    if st.button("Add Diet Plan"):
        c.execute("INSERT INTO HealthyDiets (PatientID, DoctorID, DietDescription) VALUES (?, ?, ?)", 
                  (patient_options[selected_patient], doctor_options[selected_doctor], diet_description))
        conn.commit()
        st.success("Diet plan added successfully!")

# Function to view healthy diets with patient and doctor names
def view_healthy_diets():
    st.subheader("Healthy Diets")
    query = """
    SELECT HealthyDiets.DietID, Patients.Name AS PatientName, Doctors.Name AS DoctorName, HealthyDiets.DietDescription
    FROM HealthyDiets
    JOIN Patients ON HealthyDiets.PatientID = Patients.PatientID
    JOIN Doctors ON HealthyDiets.DoctorID = Doctors.DoctorID
    """
    diets = c.execute(query).fetchall()
    df_diets = pd.DataFrame(diets, columns=["DietID", "PatientName", "DoctorName", "DietDescription"])
    st.dataframe(df_diets)

def add_calorie_entry():
    st.subheader("Add Calorie Entry")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    doctor_data = c.execute("SELECT DoctorID, Name FROM Doctors").fetchall()

    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}
    doctor_options = {f"{did}: {name}": did for did, name in doctor_data}

    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    selected_doctor = st.selectbox("Select Doctor", options=list(doctor_options.keys()))
    total_calories = st.number_input("Total Calories", min_value=0, value=0)
    date = st.date_input("Date")

    if st.button("Add Calorie Record"):
        c.execute("INSERT INTO Calories (PatientID, DoctorID, TotalCalories, Date) VALUES (?, ?, ?, ?)",
                  (patient_options[selected_patient], doctor_options[selected_doctor], total_calories, date))
        conn.commit()
        st.success("Calorie record added successfully!")

def view_calorie_entries():
    st.subheader("View Calorie Entries")
    calorie_entries = c.execute('''
        SELECT EntryID, Patients.Name AS PatientName, Doctors.Name AS DoctorName, TotalCalories, Date
        FROM Calories
        JOIN Patients ON Calories.PatientID = Patients.PatientID
        JOIN Doctors ON Calories.DoctorID = Doctors.DoctorID
    ''').fetchall()
    df_calorie_entries = pd.DataFrame(calorie_entries, columns=["EntryID", "PatientName", "DoctorName", "TotalCalories", "Date"])
    st.dataframe(df_calorie_entries)

def add_symptoms():
    st.subheader("Add Symptoms for a Patient")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}

    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    symptoms = st.text_area("Symptoms")
    duration = st.text_input("Duration of Symptoms")
    allergy = st.text_input("Known Allergies")

    if st.button("Add Symptoms"):
        c.execute("INSERT INTO Symptoms (PatientID, Symptoms, Duration, Allergy) VALUES (?, ?, ?, ?)", 
                  (patient_options[selected_patient], symptoms, duration, allergy))
        conn.commit()
        st.success("Symptoms added successfully!")

# Function to view symptoms records
def view_symptoms():
    st.subheader("View Symptoms Records")
    # Construct SQL query to fetch only the required data
    query = """
    SELECT Patients.PatientID, Patients.Name AS PatientName, Symptoms.Symptoms
    FROM Symptoms
    JOIN Patients ON Symptoms.PatientID = Patients.PatientID
    """
    # Execute SQL query and fetch data
    symptoms = c.execute(query).fetchall()
    # Create a pandas DataFrame with the fetched data
    df_symptoms = pd.DataFrame(symptoms, columns=["PatientID", "PatientName", "Symptoms"])
    # Display DataFrame in Streamlit
    st.dataframe(df_symptoms)


def add_diagnosis():
    st.subheader("Add Diagnosis for a Patient")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}
    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    result = st.text_area("Diagnosis Result")

    if st.button("Add Diagnosis"):
        c.execute("INSERT INTO Diagnosis (PatientID, Result) VALUES (?, ?)",
                  (patient_options[selected_patient], result))
        conn.commit()
        st.success("Diagnosis added successfully!")


# Function to view diagnosis records
def view_diagnosis():
    st.subheader("View Diagnosis Records")
    query = """
    SELECT Patients.Name AS PatientName, Diagnosis.Result
    FROM Diagnosis
    JOIN Patients ON Diagnosis.PatientID = Patients.PatientID
    """
    diagnosis = c.execute(query).fetchall()
    df_diagnosis = pd.DataFrame(diagnosis, columns=["PatientName", "Result"])
    st.dataframe(df_diagnosis)


# Function to add physical fitness data for a patient
def add_physical_fitness():
    st.subheader("Add Physical Fitness Data")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}

    selected_patient = st.selectbox("Select Patient for Fitness Data", options=list(patient_options.keys()))
    type_of_exercise = st.text_input("Type of Exercise")
    duration = st.text_input("Duration of Exercise")
    benefit = st.text_area("Benefits of the Exercise")

    if st.button("Add Fitness Data"):
        c.execute("INSERT INTO PhysicalFitness (PatientID, TypeOfExercise, Duration, Benefit) VALUES (?, ?, ?, ?)",
                  (patient_options[selected_patient], type_of_exercise, duration, benefit))
        conn.commit()
        st.success("Physical fitness data added successfully!")

# Function to view physical fitness records
def view_physical_fitness():
    st.subheader("View Physical Fitness Records")
    fitness = c.execute("SELECT FitnessID, Patients.Name, TypeOfExercise, Duration, Benefit FROM PhysicalFitness JOIN Patients ON PhysicalFitness.PatientID = Patients.PatientID").fetchall()
    df_fitness = pd.DataFrame(fitness, columns=["FitnessID", "PatientName", "TypeOfExercise", "Duration", "Benefit"])
    st.dataframe(df_fitness)
# Function to add dispensary data for a patient
def add_dispensary():
    st.subheader("Add Dispensary Record")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    doctor_data = c.execute("SELECT DoctorID, Name FROM Doctors").fetchall()
    prescription_data = c.execute("SELECT PrescriptionID, MedicineName FROM Prescription").fetchall()  # Assuming this table exists

    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}
    doctor_options = {f"{did}: {name}": did for did, name in doctor_data}
    prescription_options = {f"{pid}: {med}": pid for pid, med in prescription_data}

    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    selected_doctor = st.selectbox("Select Doctor", options=list(doctor_options.keys()))
    selected_prescription = st.selectbox("Select Prescription", options=list(prescription_options.keys()))
    medicine = st.text_input("Medicine")
    quantity = st.number_input("Quantity", min_value=0, value=0)

    if st.button("Add Dispensary Record"):
        c.execute("INSERT INTO Dispensary (PatientID, DoctorID, PrescriptionID, Medicine, Quantity) VALUES (?, ?, ?, ?, ?)",
                  (patient_options[selected_patient], doctor_options[selected_doctor], selected_prescription, medicine, quantity))
        conn.commit()
        st.success("Dispensary record added successfully!")

# Function to view dispensary records
def view_dispensary():
    st.subheader("View Dispensary Records")
    dispensary = c.execute("""
    SELECT DispensaryID, Patients.Name AS PatientName, Doctors.Name AS DoctorName, Prescription.MedicineName, Dispensary.Medicine, Dispensary.Quantity
    FROM Dispensary
    JOIN Patients ON Dispensary.PatientID = Patients.PatientID
    JOIN Doctors ON Dispensary.DoctorID = Doctors.DoctorID
    JOIN Prescription ON Dispensary.PrescriptionID = Prescription.PrescriptionID
    """).fetchall()
    df_dispensary = pd.DataFrame(dispensary, columns=["DispensaryID", "PatientName", "DoctorName", "PrescribedMedicine", "DispensedMedicine", "Quantity"])
    st.dataframe(df_dispensary)
# Function to add prescription data for a patient
def add_prescription():
    st.subheader("Add Prescription")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    doctor_data = c.execute("SELECT DoctorID, Name FROM Doctors").fetchall()

    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}
    doctor_options = {f"{did}: {name}": did for did, name in doctor_data}

    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    selected_doctor = st.selectbox("Select Doctor", options=list(doctor_options.keys()))
    medicine_name = st.text_input("Medicine Name")

    if st.button("Add Prescription"):
        c.execute("INSERT INTO Prescription (PatientID, DoctorID, MedicineName) VALUES (?, ?, ?)",
                  (patient_options[selected_patient], doctor_options[selected_doctor], medicine_name))
        conn.commit()
        st.success("Prescription added successfully!")

# Function to view prescription records
def view_prescriptions():
    st.subheader("View Prescriptions")
    prescriptions = c.execute("""
    SELECT Prescription.PrescriptionID, Patients.Name AS PatientName, Doctors.Name AS DoctorName, Prescription.MedicineName
    FROM Prescription
    JOIN Patients ON Prescription.PatientID = Patients.PatientID
    JOIN Doctors ON Prescription.DoctorID = Doctors.DoctorID
    """).fetchall()
    df_prescriptions = pd.DataFrame(prescriptions, columns=["PrescriptionID", "PatientName", "DoctorName", "MedicineName"])
    st.dataframe(df_prescriptions)
def add_billing():
    st.subheader("Add Billing Record")
    patient_data = c.execute("SELECT PatientID, Name FROM Patients").fetchall()
    patient_options = {f"{pid}: {name}": pid for pid, name in patient_data}

    selected_patient = st.selectbox("Select Patient", options=list(patient_options.keys()))
    mode_of_payment = st.selectbox("Mode of Payment", ["Cash", "Credit Card", "Debit Card", "Online"])
    receipt_no = st.text_input("Receipt Number")

    if st.button("Add Billing Record"):
        c.execute("INSERT INTO Billing (ModeOfPayment, PatientID, ReceiptNo) VALUES (?, ?, ?)",
                  (mode_of_payment, patient_options[selected_patient], receipt_no))
        conn.commit()
        st.success("Billing record added successfully!")
def view_billing():
    st.subheader("Billing Records")
    billing_records = c.execute("""
    SELECT Billing.BillNo, Patients.Name AS PatientName, Billing.ModeOfPayment, Billing.ReceiptNo
    FROM Billing
    JOIN Patients ON Billing.PatientID = Patients.PatientID
    """).fetchall()
    df_billing = pd.DataFrame(billing_records, columns=["BillNo", "PatientName", "ModeOfPayment", "ReceiptNo"])
    st.dataframe(df_billing)

def add_lab_test():
    st.subheader("Add Lab Test Record")
    type_of_test = st.text_input("Type of Test")
    date_of_test = st.date_input("Date of Test")

    if st.button("Add Lab Test"):
        c.execute("INSERT INTO LabTests (TypeOfTest, DateOfTest) VALUES (?, ?)",
                  (type_of_test, date_of_test))
        conn.commit()
        st.success("Lab test record added successfully!")

def view_lab_tests():
    st.subheader("Lab Test Records")
    lab_tests = c.execute("SELECT TestID, TypeOfTest, DateOfTest FROM LabTests").fetchall()
    df_lab_tests = pd.DataFrame(lab_tests, columns=["TestID", "TypeOfTest", "DateOfTest"])
    st.dataframe(df_lab_tests)


def main():
    st.title("Health And Wellness Community")
    st.sidebar.image("logo.jpeg", width=100)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    h1, .stTitle {
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)


    menu = ["Home", "Add Patient", "View Patients", "Add Doctor", "View Doctors", 
            "Add Healthy Diet", "View Healthy Diets", "Add Symptoms", "View Symptoms","Add Diagnosis", "View Diagnosis","Add Physical Fitness", "View Physical Fitness","Add Dispensary Record","View Dispensary Records","Add Prescription", "View Prescriptions","Add Billing Record", "View Billing Records", "Add Lab Test", "View Lab Tests","Add Calorie Entry", "View Calorie Entries"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the Health And Wellness Community Management System!")
        st.image("home.jpeg", width=500)
        
    elif choice == "Add Patient":
        st.image("patient.jpeg", width=150)
        add_patient()
    elif choice == "View Patients":
        st.image("patient.jpeg", width=150)
        view_patients()
    elif choice == "Add Doctor":
        st.image("doctor.jpeg", width=150)
        add_doctor()
    elif choice == "View Doctors":
        st.image("doctor.jpeg", width=150)
        view_doctors()
    elif choice == "Add Healthy Diet":
        st.image("diet.jpeg", width=200)
        add_healthy_diet()
    elif choice == "View Healthy Diets":
        st.image("diet.jpeg", width=200)
        view_healthy_diets()
    elif choice == "Add Symptoms":
        st.image("symptoms.jpeg", width=150)
        add_symptoms()
    elif choice == "View Symptoms":
        st.image("symptoms.jpeg", width=150)
        view_symptoms()
    elif choice == "Add Diagnosis":
        st.image("diag.jpeg", width=150)
        add_diagnosis()
    elif choice == "View Diagnosis":
        st.image("diag.jpeg", width=150)
        view_diagnosis()
    elif choice == "Add Physical Fitness":
        st.image("fit.jpeg", width=150)
        add_physical_fitness()
    elif choice == "View Physical Fitness":
        st.image("fit.jpeg", width=150)
        view_physical_fitness()
    elif choice == "Add Dispensary Record":
        st.image("disp.jpeg", width=150)
        add_dispensary()
    elif choice == "View Dispensary Records":
        st.image("disp.jpeg", width=150)
        view_dispensary()
    elif choice == "Add Prescription":
        st.image("prsc.jpeg", width=150)
        add_prescription()
    elif choice == "View Prescriptions":
        st.image("prsc.jpeg", width=150)
        view_prescriptions()
    elif choice == "Add Billing Record":
        st.image("bill.jpeg", width=150)
        add_billing()
    elif choice == "View Billing Records":
        st.image("bill.jpeg", width=150)
        view_billing()
    elif choice == "Add Lab Test":
        st.image("lab.jpeg", width=150)
        add_lab_test()
    elif choice == "View Lab Tests":
        st.image("lab.jpeg", width=150)
        view_lab_tests()
    elif choice == "Add Calorie Entry":
        st.image("cal.jpeg", width=150)
        add_calorie_entry()
    elif choice == "View Calorie Entries":
        st.image("cal.jpeg", width=150)
        view_calorie_entries()

# The above is the main function to call the rest of the code
if __name__ == '__main__':
    main()
