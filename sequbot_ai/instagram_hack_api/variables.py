#USER_AGENT   = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
USER_AGENT   = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'
INIT_URL     = 'https://www.instagram.com/'
LOGIN_URL    = 'https://www.instagram.com/accounts/login/ajax/'
QUERY_URL    = 'https://www.instagram.com/graphql/query/'
PROFILE_HTML = 'https://www.instagram.com/{}/'
PROFILE_URL  = 'https://www.instagram.com/{}/?__a=1'
FOLLOW_URL   = INIT_URL + 'web/friendships/{}/follow/'
UNFOLLOW_URL = INIT_URL + 'web/friendships/{}/unfollow/'
INTEGRITY_CHECKPOINT_URL = INIT_URL + 'integrity/checkpoint/?next=%2F'
CORE_HEADERS = {
    'user-agent': USER_AGENT,
    'accept-language': 'es,en-US;q=0.8,en;q=0.6,fi;q=0.4',
    'origin': 'https://www.instagram.com'
}
AJAX_HEADERS = {
    'x-instagram-ajax': 1, 
    'x-requested-with': 'XMLHttpRequest'
}
