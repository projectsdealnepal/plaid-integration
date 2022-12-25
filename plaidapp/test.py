# curl  --location --request POST
# 'https://your-institution.com/users/auth_token/' \
# --header 'Content-Type: application/x-www-form-urlencoded' \
# --header 'X-PLAID-CLIENT-ID: example_ID' \
# --header 'X-PLAID-SECRET: example_secret' \
# --header 'X-PLAID-VERSION: 2021-03-26' \
# --header 'Accept: application/json' \
# --data-urlencode 'username=user123&password=pass123&institution_id=inst123'