from django.shortcuts import render, redirect
from students.models import *
from teachers.models import *
from library.models import *
from classes.models import *
from management.models import *
from django.contrib import messages
from .models import *
from home.models import *
from account.models import *
from account.models import *
from django.utils import timezone
import os
import zipfile
from .forms import *
import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import login_required
# Create your views here.

def settings_page(request):

    setting_instance = Setting.objects.first()  # Get the single existing record (if any)

    if request.method == "POST":
        title = request.POST.get("title")
        logo = request.FILES.get("logo")

        if setting_instance:
            # ✅ Update only provided fields
            if title:
                setting_instance.title = title
            if logo:
                setting_instance.logo = logo
            setting_instance.save()
        else:
            # ✅ Create a new record if none exists
            if title or logo:  # Only create if at least one field is provided
                Setting.objects.create(
                    title=title if title else "",
                    logo=logo if logo else None
                )

        return redirect('settings:settings')  # Refresh after save

    return render(request, 'settings/setting-main.html', {
        'setting': setting_instance
    })


@login_required
def generate_backup(request):
    # Get all backups for display
    backups = SystemBackup.objects.all().order_by('-created_at')
    
    # Calculate total size
    total_size = sum(b.file_size for b in backups if b.file_size)
    
    if request.method == "POST":
        form = BackupForm(request.POST)
        
        if form.is_valid():
            description = form.cleaned_data['description']
            selected_modules = form.cleaned_data['modules']
            
            try:
                # Create backup folder with timestamp
                timestamp = timezone.now().strftime("%Y_%m_%d_%H_%M")
                base_folder = os.path.join(settings.MEDIA_ROOT, "system_backups", f"backup_{timestamp}")
                os.makedirs(base_folder, exist_ok=True)
                
                # Helper function to make Excel-safe DataFrame
                def make_excel_safe(df):
                    for col in df.columns:
                        if pd.api.types.is_datetime64_any_dtype(df[col]):
                            df[col] = df[col].apply(lambda x: x.replace(tzinfo=None) if hasattr(x, 'tzinfo') and x.tzinfo else x)
                            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    return df
                
                # Helper function to save DataFrame to Excel
                def save_to_excel(df, folder_path, filename):
                    if not df.empty:
                        df = make_excel_safe(df)
                        file_path = os.path.join(folder_path, filename)
                        df.to_excel(file_path, index=False, engine='openpyxl')
                
                # --- STUDENTS MODULE (Individual Folders) ---
                if 'students' in selected_modules:
                    students_base = os.path.join(base_folder, 'students')
                    os.makedirs(students_base, exist_ok=True)
                    
                    # Get all students
                    for student in Student.objects.all():
                        # Create student folder with name
                        student_name = f"{student.id}_{student.first_name}_{student.father_name}".replace(' ', '_')
                        student_folder = os.path.join(students_base, student_name)
                        os.makedirs(student_folder, exist_ok=True)
                        
                        # Student main info
                        student_data = Student.objects.filter(id=student.id).values()
                        if student_data:
                            df = pd.DataFrame(list(student_data))
                            save_to_excel(df, student_folder, 'student_info.xlsx')
                        
                        # Student fees info
                        fees_data = Student_fess_info.objects.filter(student=student).values()
                        if fees_data:
                            df = pd.DataFrame(list(fees_data))
                            save_to_excel(df, student_folder, 'fees_info.xlsx')
                        
                        # Student book purchases
                        books_data = BuyBook.objects.filter(student=student).values()
                        if books_data:
                            df = pd.DataFrame(list(books_data))
                            save_to_excel(df, student_folder, 'book_purchases.xlsx')
                        
                        # Student improvements
                        improve_data = StudentImporvment.objects.filter(student=student).values()
                        if improve_data:
                            df = pd.DataFrame(list(improve_data))
                            save_to_excel(df, student_folder, 'improvements.xlsx')
                        
                        # Student paid remains
                        paid_data = StudentPaidRemainAmount.objects.filter(student=student).values()
                        if paid_data:
                            df = pd.DataFrame(list(paid_data))
                            save_to_excel(df, student_folder, 'paid_remains.xlsx')
                        
                        # Student balance
                        balance_data = StudentBalance.objects.filter(student=student).values()
                        if balance_data:
                            df = pd.DataFrame(list(balance_data))
                            save_to_excel(df, student_folder, 'balance.xlsx')
                
                # --- TEACHERS MODULE (Individual Folders) ---
                if 'teachers' in selected_modules:
                    teachers_base = os.path.join(base_folder, 'teachers')
                    os.makedirs(teachers_base, exist_ok=True)
                    
                    for teacher in Teacher.objects.all():
                        # Create teacher folder with name
                        teacher_name = f"{teacher.id}_{teacher.name}".replace(' ', '_')
                        teacher_folder = os.path.join(teachers_base, teacher_name)
                        os.makedirs(teacher_folder, exist_ok=True)
                        
                        # Teacher main info
                        teacher_data = Teacher.objects.filter(id=teacher.id).values()
                        if teacher_data:
                            df = pd.DataFrame(list(teacher_data))
                            save_to_excel(df, teacher_folder, 'teacher_info.xlsx')
                        
                        # Teacher salaries
                        salary_data = TeacherPaidSalary.objects.filter(teacher=teacher).values()
                        if salary_data:
                            df = pd.DataFrame(list(salary_data))
                            save_to_excel(df, teacher_folder, 'salaries.xlsx')
                        
                        # Teacher loans
                        loan_data = TeacherLoan.objects.filter(teacher=teacher).values()
                        if loan_data:
                            df = pd.DataFrame(list(loan_data))
                            save_to_excel(df, teacher_folder, 'loans.xlsx')
                        
                        # Teacher attendance
                        attendance_data = AttendanceAndLeaves.objects.filter(teacher=teacher).values()
                        if attendance_data:
                            df = pd.DataFrame(list(attendance_data))
                            save_to_excel(df, teacher_folder, 'attendance.xlsx')
                        
                        # Teacher balance
                        balance_data = TeacherBalance.objects.filter(teacher=teacher).values()
                        if balance_data:
                            df = pd.DataFrame(list(balance_data))
                            save_to_excel(df, teacher_folder, 'balance.xlsx')
                
                # --- SUPPLIERS MODULE (Individual Folders) ---
                if 'suppliers' in selected_modules:
                    suppliers_base = os.path.join(base_folder, 'suppliers')
                    os.makedirs(suppliers_base, exist_ok=True)
                    
                    for supplier in suppliers.objects.all():
                        # Create supplier folder with name
                        supplier_name = f"{supplier.id}_{supplier.name}".replace(' ', '_')
                        supplier_folder = os.path.join(suppliers_base, supplier_name)
                        os.makedirs(supplier_folder, exist_ok=True)
                        
                        # Supplier main info
                        supplier_data = suppliers.objects.filter(id=supplier.id).values()
                        if supplier_data:
                            df = pd.DataFrame(list(supplier_data))
                            save_to_excel(df, supplier_folder, 'supplier_info.xlsx')
                        
                        # Supplier calculations
                        calc_data = ColculationWithSupplier.objects.filter(supplier=supplier).values()
                        if calc_data:
                            df = pd.DataFrame(list(calc_data))
                            save_to_excel(df, supplier_folder, 'calculations.xlsx')
                
                # --- CLASSES MODULE (Individual Folders) ---
                if 'classes' in selected_modules:
                    classes_base = os.path.join(base_folder, 'classes')
                    os.makedirs(classes_base, exist_ok=True)
                    
                    for cls in SubClass.objects.all():
                        # Create class folder with name
                        class_name = f"{cls.id}_{cls.name}".replace(' ', '_')
                        class_folder = os.path.join(classes_base, class_name)
                        os.makedirs(class_folder, exist_ok=True)
                        
                        # Class info
                        class_data = SubClass.objects.filter(id=cls.id).values()
                        if class_data:
                            df = pd.DataFrame(list(class_data))
                            
                            # Handle ManyToMany fields (convert to string)
                            if 'teacher' in df.columns:
                                teachers = ', '.join([t.name for t in cls.teacher.all()])
                                df['teacher_names'] = teachers
                            
                            if 'books' in df.columns:
                                books = ', '.join([b.name for b in cls.books.all()])
                                df['book_names'] = books
                            
                            save_to_excel(df, class_folder, 'class_info.xlsx')
                        
                        # Find students in this class
                        students_in_class = Student_fess_info.objects.filter(st_class=cls).select_related('student')
                        if students_in_class.exists():
                            student_list = []
                            for fee in students_in_class:
                                student_list.append({
                                    'student_id': fee.student.id,
                                    'student_name': fee.student.first_name,
                                    'father_name': fee.student.father_name,
                                    'fees_paid': fee.give_fees,
                                    'fees_remain': fee.remain_fees,
                                    'start_date': fee.date,
                                    'end_date': fee.end_date,
                                })
                            df = pd.DataFrame(student_list)
                            save_to_excel(df, class_folder, 'students_list.xlsx')
                
                # --- LIBRARY MODULE (Individual Book Folders) ---
                if 'library' in selected_modules:
                    library_base = os.path.join(base_folder, 'library')
                    os.makedirs(library_base, exist_ok=True)
                    
                    # Books/Items
                    items_base = os.path.join(library_base, 'books')
                    os.makedirs(items_base, exist_ok=True)
                    
                    for item in Item.objects.all():
                        book_name = f"{item.id}_{item.name}".replace(' ', '_')
                        book_folder = os.path.join(items_base, book_name)
                        os.makedirs(book_folder, exist_ok=True)
                        
                        # Book info
                        item_data = Item.objects.filter(id=item.id).values()
                        if item_data:
                            df = pd.DataFrame(list(item_data))
                            save_to_excel(df, book_folder, 'book_info.xlsx')
                        
                        # Purchases of this book
                        purchase_data = Purchase.objects.filter(item=item).values()
                        if purchase_data:
                            df = pd.DataFrame(list(purchase_data))
                            save_to_excel(df, book_folder, 'purchases.xlsx')
                        
                        # Total item info
                        total_data = TotalItem.objects.filter(item=item).values()
                        if total_data:
                            df = pd.DataFrame(list(total_data))
                            save_to_excel(df, book_folder, 'total_info.xlsx')
                    
                    # All purchases summary
                    all_purchases = Purchase.objects.all().values()
                    if all_purchases:
                        df = pd.DataFrame(list(all_purchases))
                        save_to_excel(df, library_base, 'all_purchases.xlsx')
                
                # --- ACCOUNTS MODULE (Individual User Folders) ---
                if 'accounts' in selected_modules:
                    accounts_base = os.path.join(base_folder, 'accounts')
                    os.makedirs(accounts_base, exist_ok=True)
                    
                    for user in Employee.objects.all():
                        user_name = f"{user.id}_{user.name}".replace(' ', '_')
                        user_folder = os.path.join(accounts_base, user_name)
                        os.makedirs(user_folder, exist_ok=True)
                        
                        user_data = Employee.objects.filter(id=user.id).values()
                        if user_data:
                            df = pd.DataFrame(list(user_data))
                            # Remove sensitive fields if needed
                            if 'password' in df.columns:
                                df['password'] = '***HIDDEN***'
                            save_to_excel(df, user_folder, 'user_info.xlsx')
                
                # --- FINANCE MODULE ---
                if 'finance' in selected_modules:
                    finance_base = os.path.join(base_folder, 'finance')
                    os.makedirs(finance_base, exist_ok=True)
                    
                    # All finance records
                    finance_data = FinanceRecord.objects.all().values()
                    if finance_data:
                        df = pd.DataFrame(list(finance_data))
                        save_to_excel(df, finance_base, 'finance_records.xlsx')
                    
                    # Total balance
                    balance_data = TotalBalance.objects.all().values()
                    if balance_data:
                        df = pd.DataFrame(list(balance_data))
                        save_to_excel(df, finance_base, 'total_balance.xlsx')
                    
                    # Income summary
                    income_data = FinanceRecord.objects.filter(type='income').values()
                    if income_data:
                        df = pd.DataFrame(list(income_data))
                        save_to_excel(df, finance_base, 'income_records.xlsx')
                    
                    # Expense summary
                    expense_data = FinanceRecord.objects.filter(type='expense').values()
                    if expense_data:
                        df = pd.DataFrame(list(expense_data))
                        save_to_excel(df, finance_base, 'expense_records.xlsx')
                
                # Create ZIP file
                zip_filename = f"backup_{timestamp}.zip"
                zip_path = os.path.join(settings.MEDIA_ROOT, "system_backups", zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(base_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, base_folder)
                            zipf.write(file_path, arcname)
                
                # Get file size
                file_size = os.path.getsize(zip_path)
                
                # Get client IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                
                # Save backup record
                SystemBackup.objects.create(
                    created_by=request.user,
                    backup_file=f"system_backups/{zip_filename}",
                    file_size=file_size,
                    description=description,
                    ip_address=ip_address
                )
                
                # Clean up temporary folder
                import shutil
                shutil.rmtree(base_folder)
                
                messages.success(request, 'پشتیبان‌گیری با موفقیت انجام شد!')
                
            except Exception as e:
                messages.error(request, f'خطا در پشتیبان‌گیری: {str(e)}')
            
            return redirect('settings:generate_backup')
    else:
        form = BackupForm()
    
    context = {
        'form': form,
        'backups': backups,
        'total_size': total_size,
    }
    
    return render(request, 'settings/back-up.html', context)


@login_required
def delete_backup(request, backup_id):
    if request.method == "POST":
        try:
            backup = SystemBackup.objects.get(id=backup_id)
            
            # Delete file
            if backup.backup_file:
                file_path = os.path.join(settings.MEDIA_ROOT, backup.backup_file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Delete record
            backup.delete()
            
            messages.success(request, 'پشتیبان با موفقیت حذف شد!')
        except SystemBackup.DoesNotExist:
            messages.error(request, 'پشتیبان یافت نشد!')
        except Exception as e:
            messages.error(request, f'خطا در حذف: {str(e)}')
    
    return redirect('settings:generate_backup')