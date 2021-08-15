from datetime import date, datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from fpdf import FPDF
import mysql
import mysql.connector
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):

    return  render(request,"trainer.html")

def store(request):
    college = request.POST["college"]
    fromdate = request.POST["fromdate"]
    todate = request.POST["todate"]
    session = request.POST["session"]
    mode = request.POST["mode"]
    fees = request.POST["fees"]
    trainer = request.POST["trainer"]
    mydb = mysql.connector.connect(host="localhost", user="root", password="", database="invoice")
    print(mydb)
    if (mydb):
        print("Connection successful")
    else:
        print("Connection import unsuccessful")
    year = int(todate.split("-")[0])
    month = int(todate.split("-")[1])

    day = int(todate.split("-")[2])
    year1 = int(fromdate.split("-")[0])
    month1 = int(fromdate.split("-")[1])

    day1 = int(fromdate.split("-")[2])
    n = (date(year, month, day) - date(year1, month1, day1)).days
    totalpay = int(fees) * (n+1)
    if mode=="Offline":
        totalpay=(n+1)*150
    mycursor = mydb.cursor()
    mycursor.execute("select location from college_details where name='" + college + "'")
    dblocation = mycursor.fetchone()[0]
    mycursor.execute("select location from trainer_deatils where name='" + trainer + "'")
    trainerloc = mycursor.fetchone()[0]
    travel = 0
    if dblocation != trainerloc and mode == "Offline":
        totalpay = totalpay + 1000
        travel = 1
        results = "Confirmation mail sent. Total Pay= " + str(totalpay)
    else:
        results = "Confirmation mail sent. Total Pay= " + str(totalpay)
    food = 1
    if mode=="Online":
        food=0
    else:
        totalpay=150*(n+1)
    email_generator(college, fees, session, n, mode, fromdate, todate, trainer, travel, food, totalpay)
    return render(request, "trainer.html", {"res": results})

def email_generator(college, fees, session, n, mode, fromdate, todate, trainer,travel, food, totalpay):
    # set up the SMTP server
    s = SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login("enter email @gmail.com", "enter app specific password")

    # For each contact, send the email:
    for name, email in [("Infinity","enter email @gmail.com")]:
        msg = MIMEMultipart()  # create a message

        # add in the actual person name to the message template
        message = "Dear "+trainer+",\n\nThis is your confirmation mail from Genesis. Following are the details:\n\nName of college: "+college+"\nRemuneration: "+fees+"\nSession: "+session+"\nNumber of days: "+str(n)+"\nMode: "+mode+"\nDates: "+fromdate+" to "+todate

        # setup the parameters of the message
        msg['From'] = "enter email @gmail.com"
        msg['To'] = "enter email @gmail.com"
        msg['Subject'] = "Genesis - Confirmation Mail!"
        pdf_generator(college, fees, session, n, mode, fromdate, todate, trainer, travel, food, totalpay)
        with open("invoice.pdf",'rb') as file:
            attach=MIMEApplication(file.read(), _subtype='pdf')
        attach.add_header("Content-Disposition","attachment",filename=str("invoice.pdf"))
        msg.attach(attach)
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)

        del msg


def pdf_generator(college, fees, session, n, mode, fromdate, todate, trainer, travel, food, totalpay):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font( 'Arial', 'B', 14 )
    pdf.image( "https://www.genesistraining.in/images/logo.png", x=160, y=20, w=30, h=40 )
    mydb = mysql.connector.connect( host="localhost", user="root", password="", database="invoice" )
    mycursor = mydb.cursor()
    mycursor.execute( "select trainer_id from trainer_deatils where name='" + trainer + "'" )
    trainer_id = mycursor.fetchone()[0]
    mycursor.execute( "select phone_number from trainer_deatils where name='" + trainer + "'" )
    phone = mycursor.fetchone()[0]
    mycursor.execute( "select pan from trainer_deatils where name='" + trainer + "'" )
    pan = mycursor.fetchone()[0]
    mycursor.execute( "select email_id from trainer_deatils where name='" + trainer + "'" )
    email_id = mycursor.fetchone()[0]
    mycursor.execute( "select location from trainer_deatils where name='" + trainer + "'" )
    location = mycursor.fetchone()[0]
    mycursor.execute( "select acc_num from bank_details where trainer_id=" + str( trainer_id ) )
    acc_num = mycursor.fetchone()[0]
    mycursor.execute( "select ifsc_code from bank_details where trainer_id=" + str( trainer_id ) )
    ifsc = mycursor.fetchone()[0]
    mycursor.execute( "select bank_name from bank_details where trainer_id=" + str( trainer_id ) )
    bank_name = mycursor.fetchone()[0]
    pdf.cell( 200, 10, txt="Genesis Invoice Generation", ln=1, align='C' )
    pdf.set_font( 'Arial', '', 11 )
    pdf.cell( 200, 10, txt="Name of trainer: " + str( trainer ), ln=3 )
    pdf.cell( 200, 10, txt="Account Number: " + str( acc_num ), ln=5 )
    pdf.cell( 200, 10, txt="IFSC Code: " + str( ifsc ), ln=7 )
    pdf.cell( 200, 10, txt="Bank Name: " + str( bank_name ), ln=9 )
    pdf.cell( 200, 10, txt="Phone Number: " + str( phone ), ln=11 )
    pdf.cell( 200, 10, txt="Pan: " + str( pan ), ln=13 )
    pdf.cell( 200, 10, txt="Email ID: " + str( email_id ), ln=15 )
    pdf.cell( 200, 10, txt="Base Location: " + str( location ), ln=17 )
    Dates = []
    temp = fromdate
    for i in range( n ):
        s = datetime.strptime( fromdate, '%Y-%m-%d' )
        s = s + timedelta( i )
        Dates.insert( i, str( s.date() ) )
    data = [['Date', 'College', 'Fee/Day', 'Travel Allowance', 'Food Allowance']]
    for i in range( n ):
        if i == 0 or i == n:
            if travel == 1:
                if food == 1:
                    data.insert( i + 1, [Dates[i], college, fees, "500", "150"] )
                else:
                    data.insert( i + 1, [Dates[i], college, fees, "500", "---"] )
            else:
                if food == 1:
                    data.insert( i + 1, [Dates[i], college, fees, "---", "150"] )
                else:
                    data.insert( i + 1, [Dates[i], college, fees, "---", "---"] )
        else:
            if food == 1:
                data.insert( i + 1, [Dates[i], college, fees, "---", "150"] )
            else:
                data.insert( i + 1, [Dates[i], college, fees, "---", "---"] )
    if food == 1:
        f = 150 * (n + 1)
    else:
        f = 0
    if travel == 1:
        t = 500 * 2
    else:
        t = 0
    tf = int( fees ) * (n + 1)
    col_width = pdf.w / 5.6
    spacing = 1
    row_height = pdf.font_size * 2
    for row in data:
        for item in row:
            pdf.cell( col_width, row_height * spacing, txt=item, border=1, align="C" )
        pdf.ln( row_height * spacing )
    pdf.cell( col_width * 2, row_height * spacing, txt="Total", border=1, align="C" )
    pdf.cell( col_width, row_height * spacing, txt=str( tf ), border=1, align="C" )
    pdf.cell( col_width, row_height * spacing, txt=str( t ), border=1, align="C" )
    pdf.cell( col_width, row_height * spacing, txt=str( f ), border=1, align="C" )
    pdf.ln( row_height * spacing )
    pdf.cell( col_width * 4, row_height * spacing, txt="Grand Total", border=1, align="C" )
    pdf.cell( col_width, row_height * spacing, txt=str( totalpay ), border=1, align="C" )

    pdf.output( "invoice.pdf" )