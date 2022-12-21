import tkinter as tk

def calculate():
    amount = int(principal.get())
    interest = float(rate.get())/1200
    period = float(years.get())*12
    emi.set(amount * interest * (pow((1+interest),period)/(pow((1+interest),period)-1)))


main_window = tk.Tk()
tk.Label(main_window, text='Amount',padx=10,pady=10).grid(row=0)
tk.Label(main_window, text='Interest',padx=10,pady=10).grid(row=1)
tk.Label(main_window, text='Tenure',padx=10,pady=10).grid(row=2)
tk.Button(main_window,text='Calculate',command=calculate,padx=10,pady=10).grid(row=3,columnspan=2)
tk.Label(main_window, text='EMI',padx=10,pady=10).grid(row=4)

tk.Label(main_window, text='Total Interest',padx=10,pady=10).grid(row=6)

tk.Label(main_window, text='Total Amount',padx=10,pady=10).grid(row=8)

principal = tk.StringVar(main_window)
rate = tk.StringVar(main_window)
years = tk.StringVar(main_window)
emi = tk.StringVar(main_window)
total_interest = tk.StringVar(main_window)
total_payment = tk.StringVar(main_window)
emi.set(0)
total_interest.set(0)
total_payment.set(0)
tk.Label(main_window, textvariable=emi,font=("Arial", 24),padx=10,pady=10).grid(row=5)
tk.Label(main_window, textvariable=total_interest,font=("Arial", 24),padx=10,pady=10).grid(row=7)
tk.Label(main_window, textvariable=total_payment,font=("Arial", 24),padx=10,pady=10).grid(row=9)
tk.Entry(main_window,textvariable=principal).grid(row=0, column=1)
tk.Entry(main_window,textvariable=rate).grid(row=1, column=1)
tk.Entry(main_window,textvariable=years).grid(row=2, column=1)

main_window.mainloop()