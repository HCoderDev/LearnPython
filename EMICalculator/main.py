import tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
chart_widget=None
def calculate():
    input_principal = int(principal.get())
    input_rate = float(rate.get())/1200
    input_tenure = float(years.get())*12
    emi_value = input_principal * input_rate * (pow((1+input_rate),input_tenure)/(pow((1+input_rate),input_tenure)-1))
    emi.set('{:.2f}'.format(emi_value))

    total_payment_value = emi_value * input_tenure
    total_interest_value = total_payment_value - input_principal
    total_interest.set('{:.2f}'.format(total_interest_value))
    total_payment.set('{:.2f}'.format(total_payment_value))

    label = [f'Interest({"{:.2f}".format(total_interest_value)})',f'Principal ({input_principal})']
    values = [total_interest_value,input_principal]

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.pie(values,radius=1,labels=label,shadow=False)
    global chart_widget

    if chart_widget is not None:
        chart_widget.pack_forget()

    final_chart = FigureCanvasTkAgg(fig,frameChart)
    chart_widget = final_chart.get_tk_widget()
    chart_widget.pack()



main_window = Tk.Tk()
main_window.title("EMI Calculator using python")
main_window.geometry("")

Tk.Label(main_window, text='Amount', padx=10, pady=10).grid(row=0)
Tk.Label(main_window, text='Interest', padx=10, pady=10).grid(row=1)
Tk.Label(main_window, text='Tenure', padx=10, pady=10).grid(row=2)
Tk.Button(main_window, text="Calculate", command=calculate, padx=10, pady=10).grid(row=3, columnspan=2)

principal = Tk.IntVar(main_window)
rate = Tk.StringVar(main_window)
years = Tk.StringVar(main_window)
emi = Tk.StringVar(main_window)
total_interest = Tk.StringVar(main_window)
total_payment = Tk.StringVar(main_window)
principal.set(0)
rate.set(0)
years.set(0)
emi.set(0)
total_interest.set(0)
total_payment.set(0)

Tk.Entry(main_window, textvariable=principal).grid(row=0, column=1)
Tk.Entry(main_window, textvariable=rate).grid(row=1, column=1)
Tk.Entry(main_window, textvariable=years).grid(row=2, column=1)
Tk.Label(main_window, text='EMI', padx=10, pady=10).grid(row=4, columnspan=2)
Tk.Label(main_window, textvariable=emi, font=('Arial', 16), padx=10, pady=10).grid(row=5, columnspan=2)
Tk.Label(main_window, text='Total Interest', padx=10, pady=10).grid(row=6, columnspan=2)
Tk.Label(main_window, textvariable=total_interest, font=('Arial', 16), padx=10, pady=10).grid(row=7, columnspan=2)
Tk.Label(main_window, text='Total Amount', padx=10, pady=10).grid(row=8, columnspan=2)
Tk.Label(main_window, textvariable=total_payment, font=('Arial', 16), padx=10, pady=10).grid(row=9, columnspan=2)

frameChart = Tk.Frame(main_window)
frameChart.grid(row=1,column=2,rowspan=10)

main_window.mainloop()
