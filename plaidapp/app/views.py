from django.shortcuts import render, redirect
from django.views.defaults import page_not_found
from . import plaid_api
import pandas as pd
from django.contrib.auth.models import User
from .models import Accounts
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect
import os
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as auth_login
from sms import send_sms
from django.utils.crypto import get_random_string



# Redirect to a success page.
# from django.shortcuts import redirect

# Create your views here.
TWILIO_NUMBER = '+19733557187'
CLIENT = plaid_api.plaid_connect()
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')
RECIPIENT = '+977-9840560847'

# PUBLIC_TOKEN = CLIENT.PUBLIC_TOKEN
# ACCESS_TOKEN = CLIENT.ACCESS_TOKEN

def get_bank_accounts(institution_id='', bank_name=''):
    CLIENT.get_public_token_access(institution_id=institution_id)
    CLIENT.get_access_token()
    '''
    NOTE: check username and password here.
    '''
    ##act_numbers_in_bank = CLIENT.auth()
    # print(act_numbers_in_bank.keys)
    accounts = CLIENT.get_accounts()
    # keys = ['ach', 'eft', 'bacs', 'international']
    # account_numbers = []
    # for k in keys:
    #     bank_type = act_numbers_in_bank[k]
    #     for v in bank_type:
    #         fields = {}
    #         type_ = k
    #         account_no = v['account']
    #         account_no_ = []
    #         for i, n in enumerate(account_no[::-1]):
    #             if i <= 3:
    #                 account_no_.append(n)
    #             else:
    #                 account_no_.append('*')
    #         account_display = ''.join(account_no_[::-1])
    #         fields['type'] = type_
    #         fields['account_display'] = account_display
    #         fields['account'] = account_no
    #         fields['act_id'] = v['account_id']
    #         fields['routing'] = v['routing']
    #         account_numbers.append(fields)
    # df_account = pd.DataFrame(account_numbers)
    # df_account = df_account.set_index('act_id')
    ac_names = []
    for ac in accounts:
        mask = ac.get('mask')
        ac_names.append({
            'name': ac.get('name'),
            'off': ac.get('official_name'),
            'subtype': ac.get('subtype'),
            'type': ac.get('type'),
            'available': ac['balances']['available'],
            'current': ac['balances']['current'],
            'act_id': ac.get('account_id'),
            'mask': mask,
            'acc_no': f'************{mask}',
            'bank': bank_name
        })
    # df_account_names = pd.DataFrame(ac_names)
    # df_account_names = df_account_names.set_index('act_id')
    # df_final = pd.merge(df_account_names, df_account, right_index=True, left_index=True)
    # df_final = df_final.reset_index('act_id')
    # df_final['bank'] = bank_name
    # account_details = df_final.to_dict('records')
    # return account_details
    return ac_names


def get_account_details(username):
    pass


def index(request):
    print('Here')
    return render(request, template_name='test.html', context={})


def signin(request):
    template = 'register/login.html'
    context = {
        'otp': False
    }
    if request.method == 'POST':
        log_in = request.POST.get('login')
        otp = request.POST.get('submit')
        resend = request.POST.get('resend')

        if resend:
            rand_no = get_random_string(length=6, allowed_chars='1234567890')
            # valid = send_sms(f'The OTP:{rand_no}', TWILIO_NUMBER, [RECIPIENT])
            valid = True
            if valid:
                context['otp'] = True
                context['code'] = rand_no
                request.session[request.user.username] = {
                    'no': rand_no
                }
                return render(request, template_name=template, context=context)

        if otp:
            otp_code = request.POST['otp_code']
            # print('Here', request.user.username)
            # print(otp_code, request.session[request.user.username]['no'])
            if otp_code == request.session[request.user.username]['no']:
                return HttpResponseRedirect('/select/')
            else:
                context['code'] = otp_code
                context['error'] = 'Invalid Code.'
                context['otp'] = True
                return render(request, template_name=template, context=context)

        if log_in:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            context['username'] = username
            if user is not None:
                rand_no = get_random_string(length=6, allowed_chars='1234567890')
                # valid = send_sms(f'The OTP:{rand_no}', TWILIO_NUMBER, [RECIPIENT])
                print(rand_no)
                valid = 1
                if valid:
                    auth_login(request, user)
                    request.session[username] = {
                        'no': rand_no
                    }
                    context['otp'] = True
                    context['code'] = rand_no
                    return render(request,template_name=template,context=context)
            else:
                context['error'] = 'Invalid username/password.'

    return render(request, template_name=template, context=context)


def register(request):
    template = 'register/register.html'

    if request.user.is_authenticated:
        context = {
            'title': 'Create User',
        }

        msg = ''
        context['username'] = 'joe@gmail.com'
        context['password'] = ''
        context['email'] = ''
        context['firstname'] = ''
        context['lastname'] = ''
        context['fields'] = Accounts.objects.filter(acc_id=request.user.username)
        if request.method == 'POST':
            # login = request.POST.get('login')
            register = request.POST.get('signup')
            if register:
                firstname = request.POST.get('first')
                lastname = request.POST.get('last')
                email = request.POST.get('email')
                username = request.POST.get('username')
                password = request.POST.get('password')
                checkbox = request.POST.get('user_type')
                superuser = 0
                role = 'user'
                if checkbox == "on":
                    superuser = 1
                    role = 'admin'

                # repass = request.POST.get('repass')

                if firstname and lastname and email and username and password:
                    context['username'] = username
                    context['password'] = password
                    # context['repass'] = repass
                    context['email'] = email
                    context['firstname'] = firstname
                    context['lastname'] = lastname
                    user_name = User.objects.filter(username=username).first()
                    if not user_name:
                        # if password == repass:
                        kwargs = {
                            'first_name': firstname,
                            'last_name': lastname,
                            'username': username,
                            'email': email,
                            'password': make_password(password=password),
                            'is_superuser': superuser
                        }
                        obj = User(**kwargs)
                        obj.save()
                        msg = f'User: {username} created Successfully. Role type: {role}'
                        # else:
                        #     msg = f'Password not Matched'
                    else:
                        msg = f'Username Already Exists.'
                else:
                    msg = 'Fields Missing.'

                context['error'] = msg
                return render(request, template_name=template, context=context)

            # if login:
            #     if 'username' not in request.session:
            #         '''
            #         Check credentials here
            #         '''
            #
            #         username = request.POST.get('username')
            #         password = request.POST.get('password')
            #
            #         if username and password:
            #
            #             context['username'] = username
            #             context['password'] = password
            #             user_name = User.objects.filter(username=username).first()
            #             print(user_name)
            #             if user_name:
            #                 previous_password = user_name.password
            #                 check_ = check_password(password, previous_password)
            #                 if check_:
            #                     request.session['username'] = username
            #                     template = 'index.html'
            #                 else:
            #                     msg = f'Incorrect Password.'
            #             else:
            #                 msg = 'Username doesn''t exists.'
            #
            #         else:
            #             msg = f'Incorrect username or password.'
            #         context['error'] = msg
            #
            #         return render(request, template_name=template, context=context)
            #     else:
            #
            #         return HttpResponseRedirect('/select/')
        return render(request, template, context=context)
    else:
        return HttpResponseRedirect('/signin/')


# def institution(request):
#     template = 'account/select.html'
#     context = {}
#
#     bank_names = get_institutions(client=client)
#     bank_info = []
#     for bank in bank_names:
#         bank_info.append({
#             'id': bank.get('institution_id'),
#             'name': bank.get('name')
#         })
#     return render(request, template, context={
#         'bank_info': bank_info
#     })


def login(request):
    template = 'register/login.html'
    context = {}
    bank = request.GET.get('bank')
    ins_id = request.GET.get('id')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        ins_id = request.POST.get('ins_id')
        if username and password:
            '''
            check username and authenticate user.
            '''
            template = 'index.html'
            public_token = get_public_token_access(client=client, INSTITUTION_ID=ins_id)
            access_token = get_access_token(public_token=public_token, client=client)
            accounts = get_accounts(access_token=access_token, client=client)
            ac_names = []
            for ac in accounts:
                ac_names.append({
                    'name': ac.get('name'),
                    'off': ac.get('official_name'),
                    'subtype': ac.get('subtype'),
                    'type': ac.get('type'),
                    'available': ac['balances']['available'],
                    'current': ac['balances']['current'],
                    'act_id': ac.get('account_id')
                })
            context = {
                'bank': bank,
                'id': ins_id,
                'acc': ac_names

            }
            return render(request, template, context=context)

        else:
            error = 'Invalid username and password.'

    if bank:
        return render(request, template, context={
            'bank': bank,
            'id': ins_id,
            'error': error
        })
    else:
        return render(request, page_not_found)


def accounts(request):
    all_banks = []
    account_details = []
    bank_name = request.GET.get('bank', None)
    select = 2
    if request.user.is_authenticated:
        session_user = request.user.username
        acc_fields = Accounts.objects.filter(acc_id=session_user)
        if bank_name:
            for acc in acc_fields:
                if acc.bank_name == bank_name:
                    institution_id = acc.institution_id
                    all_banks.append(acc.bank_name)
                    break
        else:
            acc = acc_fields[0]
            institution_id = acc.institution_id
            bank_name = acc.bank_name

        account_details = get_bank_accounts(institution_id=institution_id, bank_name=bank_name)

        template = 'index.html'
        login = request.POST.get('login')
        act_id = request.GET.get('act_id')
        context = {
            'select': 0,
            'error': ''
        }

        if request.POST.get('search_field') == 'search':
            search_field = request.POST.get('input_search')
            bank_names = CLIENT.get_institutions()
            bank_info = []
            bank_infos = []
            state = False
            for bank in bank_names:
                if bank.get('name').lower() == search_field.lower():
                    bank_info.append({
                        'id': bank.get('institution_id'),
                        'name': bank.get('name')
                    })
                    state = True
                else:
                    bank_infos.append({
                        'id': bank.get('institution_id'),
                        'name': bank.get('name')
                    })

            if not state:
                bank_info = bank_infos

            context.update({
                'bank_info': bank_info,
                'fields': acc_fields,
                'name': bank_name,
                'select': 1,
                # 'bank': account_details
            })

            return render(request,
                          template,
                          context=context
                          )

        if login:
            username = request.POST.get('username')
            password = request.POST.get('password')
            # print(username, password)
            if username and password:
                '''
                Verify Username and Password.
                '''
                institution_id = request.POST.get('ins_id')
                bank_name = request.POST.get('bank_name')
                account_details = get_bank_accounts(institution_id=institution_id, bank_name=bank_name)
                context = {
                    'username': username,
                    'bank': account_details,
                    'id': institution_id,
                    'select': 2,
                    'name': bank_name,
                    'fields': acc_fields,
                    # 'acc': ac_names

                }

                acc_id = User.objects.filter(username=session_user).first()
                print(acc_id)
                kwargs = {
                    'acc_id': acc_id,
                    'bank_name': bank_name,
                    'user_name': username,
                    'user_pass': password,
                    'institution_id': institution_id,
                    # 'fields': acc_fields,
                    'verified': 1
                }
                check = Accounts.objects.filter(acc_id=acc_id, bank_name=bank_name)
                print(check, 'Here')
                if not check:
                    act_obj = Accounts(**kwargs)
                    act_obj.save()


            else:
                msg = 'Invalid Credentials'

            return render(request, template, context=context)

        else:
            pass

        # else:
        #     if request.get_full_path() == '/select/':

        if act_id:
            template = 'index.html'
            institution_id = request.GET.get('ins_id')
            transaction = CLIENT.get_transaction()

            '''
            GET From DB.
            '''
            ac_names = [{
                'name': 'KFC',
                'merchant_name': 'KFC Restuarent',
                'date': '2021-06-18',
                'amount': '20',
            },
                {
                    'name': 'Apple',
                    'merchant_name': 'Apple Store',
                    'date': '2021-06-18',
                    'amount': '300',
                }
            ]
            if transaction:
                for ac in transaction:
                    if ac.get('account_id') == act_id:
                        ac_names.append({
                            'name': ac.get('name'),
                            'merchant_name': ac.get('merchant_name'),
                            'date': ac.get('authorized_date'),
                            'amount': ac.get('amount'),
                            # 'type': ac.get('type'),
                            # 'available': ac['balances']['available'],
                            # 'current': ac['balances']['current'],
                            # 'act_id': ac.get('account_id')
                        })

            context = {
                'transaction': ac_names,
                # 'id': ins_id,
                'head': 'No Transactions' if not ac_names else '',
                'fields': acc_fields,
                'select': 0

            }
            return render(request, template, context=context)
        context = {
            'bank': account_details,
            'fields': acc_fields,
            'name': bank_name
        }
        return render(request, template, context=context)
    else:
        return render(request, 'index.html')


def connect(request):
    template = 'index.html'
    context = {}
    bank_names = CLIENT.get_institutions()
    bank_info = []
    for bank in bank_names:
        bank_info.append({
            'id': bank.get('institution_id'),
            'name': bank.get('name')
        })
    context.update({
        'bank_info': bank_info,
        'select': 1
    })

    return render(request,
                  template,
                  context=context
                  )


def transaction(request):
    template = 'account/transaction.html'
    context = {}
    if request.user.is_authenticated:
        session_user = request.user.username
        acc_fields = Accounts.objects.filter(acc_id=session_user)
        context = {
            'fields': acc_fields,
        }
        return render(request, template, context=context)


def change_password(request):
    template = 'register/password.html'
    if request.user.is_authenticated:
        session_user = request.user.username
        acc_fields = Accounts.objects.filter(acc_id=session_user)
        context = {
            'fields': acc_fields,
        }
        return render(request, template_name=template, context=context)
    else:
        return HttpResponseRedirect('/signin/')


def profile(request):
    template = 'register/profile.html'
    bank_name = None
    all_banks = []
    if request.user.is_authenticated:
        session_user = request.user.username
        acc_fields = Accounts.objects.filter(acc_id=session_user)

        profile_details = User.objects.filter(username=request.user.username).first()

        context = {
            'details': profile_details,
            'username': session_user,
            'fields': acc_fields,
        }

        return render(request, template_name=template, context=context)
    else:
        return HttpResponseRedirect('/login/')


def logout_view(request):
    logout(request)

    return HttpResponseRedirect('/signin/')

    # print('here',request.user.is_authenticated)


def login_success(request):
    print(request.user.is_verified())
    if request.user.is_verified():
        return render(request, 'index.html', context={})
    else:
        return HttpResponseRedirect("two_factor:setup")
