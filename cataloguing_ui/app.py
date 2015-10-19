import json
import config
import ast

from flask import Flask, jsonify, render_template, request, url_for, session, redirect, Blueprint, flash
from flask_oauthlib.client import OAuth
from flask_oauth2_login import GoogleLogin
from pymongo import MongoClient
from bson.objectid import ObjectId

from utils import update_category, get_categories, get_product_tagging_details, get_vendors, get_subcategories, get_taglist, get_all_tags, inc_skip_count, add_new_subcat
from users import add_user, get_tag_count, inc_tag_count, dcr_tag_count, get_users

bp = Blueprint('bp', __name__, static_folder='static', template_folder='templates')
app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY

client = MongoClient(config.MONGO_IP, 27017)
db = client.products_db
oauth = OAuth()

############################------Google Login------####################################

app.config.update(
  GOOGLE_LOGIN_REDIRECT_SCHEME="http",
)

app.config['GOOGLE_LOGIN_CLIENT_ID'] = config.GOOGLE_CLIENT_ID
app.config['GOOGLE_LOGIN_CLIENT_SECRET'] = config.GOOGLE_CLIENT_SECRET

google_login = GoogleLogin(app)

@bp.route('/google-redirect')
def redirect_google():
    return redirect(google_login.authorization_url())

@google_login.login_success
def login_success(token, profile):
    if profile:

        domain = profile['email'].split('@')[1]
        if domain in config.ALLOWED_DOMAINS or profile['email'] in config.WHITELIST:
            add_user(profile)
            session['is_admin'] = False
            session['user'] = profile
            
            if profile['email'] in config.ADMINS:
                session['is_admin'] = True
            return redirect(url_for('bp.tag', q='tag'))

        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('bp.login'))

    else:
        print('Login failed.')
        return "Login failed"
        
@google_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))

############################------Facebook Login------##################################

# facebook = oauth.remote_app('facebook',
#                             base_url='https://graph.facebook.com/',
#                             request_token_url=None,
#                             access_token_url='/oauth/access_token',
#                             authorize_url='https://www.facebook.com/dialog/oauth',
#                             consumer_key=config.FB_CONSUMER_KEY,
#                             consumer_secret=config.FB_CONSUMER_SECRET,
#                             request_token_params={'scope': 'email'})


# @bp.route('/login/fbauthorized')
# @facebook.authorized_handler
# def facebook_authorized(resp):
#     if resp is None:
#         return 'Access denied: reason=%s error=%s' % (
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     print('access_token')
#     print(resp['access_token'])
#     session['oauth_token'] = (resp['access_token'], '')

#     me = facebook.get('/me')
#     print(me.data)
#     add_user(me.data)
#     session['is_admin'] = False
#     if me.data['id'] and me.data['name'] and me.data['email']:
#         session['user'] = me.data
#         if me.data['email'] in config.ADMINS:
#             session['is_admin'] = True
#         return redirect(url_for('bp.tag', q='tag'))
#     else:
#         return "Login failed"


# @facebook.tokengetter
# def get_facebook_oauth_token():
#     return session.get('oauth_token')


# @bp.route('/fb-login')
# def fb_login():
#     """
#     The facebook login page. Clears the session before allowing a new user to authenticate.
#     """
#     print("login attempt")
#     session.clear()
#     print(request.args.get('next'))
#     return facebook.authorize(callback=url_for('bp.facebook_authorized',
#                                                next=request.args.get('next') or request.referrer or None,
#                                                _external=True))

###########################------Facebook Login Ends Here------#################################

@bp.route('/')
def index():
    return redirect(url_for('bp.login'))

@bp.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Render the simple login page having signin icons
    '''
    if 'user' in session:
        return redirect(url_for('bp.tag', q='tag'))
    return render_template('login.htm')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp.login'))

@bp.route('/tagging', methods=['POST', 'GET'])
def tag():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        q = request.args.get('q') 
        
        if (not session['is_admin']) and (q == 'verify' or q == '3-skips'):
            flash('Invalid credentials', 'error')
            return redirect(url_for('bp.login'))
        
        price_range_text_list = config.PRICE_RANGE_TEXT_LIST
        price_range_value_list = config.PRICE_RANGE_VALUE_LIST

        return render_template('tag_product.html',
                               vendors=get_vendors(),
                               available_cats=get_categories(),
                               available_cats1=get_categories(),
                               price_range_text_list=price_range_text_list,
                               price_range_value_list=price_range_value_list,
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count,
                               q=q,
                               autoescape=False)
    else:
        return redirect(url_for('bp.login'))

@bp.route('/get-products', methods=['GET', 'POST'])
def get_products():
    posted_data = request.get_json()
    if 'price' in posted_data:
        posted_data['price'] = ast.literal_eval(posted_data['price'])
    q = posted_data.pop('q', None)

    if 'vendor' in posted_data and posted_data['vendor'] == 'All':
        posted_data.pop('vendor', None)
    if q == 'tag':
        tagging_info = get_product_tagging_details(posted_data)
    if q == 'verify':
        tagging_info = get_product_tagging_details(posted_data, True)
    if q == '3-skips':
        tagging_info = get_product_tagging_details(posted_data, False, True)

    return json.dumps(tagging_info)

@bp.route('/get-subcats', methods=['GET', 'POST'])
def get_subcats():
    posted_data = request.get_json()
    print(posted_data)
    return get_subcategories(posted_data['category_id'])

@bp.route('/change-category', methods=['GET', 'POST'])
def change_category():
    posted_data = request.get_json()
    print(posted_data)
    update_category(posted_data['id'], posted_data['category'], posted_data['subcat'])
    tag_list = get_taglist(posted_data['category'])
    tag_list.update(get_taglist(posted_data['subcat']))
    return json.dumps(tag_list)

@bp.route('/set-tags', methods=['GET', 'POST'])
def set_tags():
    posted_data = request.get_json()
    q = posted_data.pop('q', None)
    print('############posted_data###########', posted_data)
    id = posted_data.pop("id", None)
    user_id = session['user']['id']
    posted_data['tagged_by'] = user_id

    if posted_data['tags'] and (posted_data['is_dang'] or posted_data['is_xray'] or posted_data['is_dirty']):
        posted_data['done'] = True

    next_name = {}
    if 'category' in posted_data:
        next_name['category'] = posted_data.pop("category")
    if 'vendor' in posted_data:
        vendor = posted_data.pop("vendor")
        if vendor != 'All':
            next_name['vendor'] = vendor
    if 'price' in posted_data:
        next_name['price'] = ast.literal_eval(posted_data.pop('price'))

    undo = posted_data.pop("undo", None)
    if undo:
        next_name.clear()
        next_name['_id'] = ObjectId(id)

    elif posted_data.pop("is_skipped"):
        inc_skip_count(id)

    else:
        print('####id####data to be saved -- tagged -- ####', id, posted_data)        
        db.products.update({'_id': ObjectId(id)}, {"$set": posted_data})
        inc_tag_count(user_id)

    #fetching next product tagging info
    tagging_info = get_product_tagging_details(next_name)

    if undo:
        db.products.update({'_id': ObjectId(id)},{"$unset":{'is_dang':'','is_dirty':'','is_xray':'',
                            'tags':'','tagged_by':'','epoch':'','done':''}})
        dcr_tag_count(user_id)

    tag_count, verify_count = get_tag_count(user_id)
    tagging_info['tag_count'] = tag_count
    tagging_info['verify_count'] = verify_count
    return json.dumps(tagging_info)

@bp.route('/set-verified-tags', methods=['GET', 'POST'])
def set_verified_tags():
    posted_data = request.get_json()
    q = posted_data.pop('q', None)
    print('############posted_data###########', posted_data)
    id = posted_data.pop("id", None)
    user_id = session['user']['id']
    posted_data['verified_by'] = user_id
    posted_data['verified'] = True

    next_name = {}
    if 'category' in posted_data:
        next_name['category'] = posted_data.pop("category")
    if 'vendor' in posted_data:
        vendor = posted_data.pop("vendor")
        if vendor != 'All':
            next_name['vendor'] = vendor
    if 'price' in posted_data:
        next_name['price'] = ast.literal_eval(posted_data.pop('price'))

    undo = posted_data.pop("undo", None)
    if undo:
        print('i wanto see last product please........................................')
        next_name.clear()
        next_name['_id'] = ObjectId(id)
        
    elif posted_data.pop("is_skipped"):
        admin_skip_keys = ['verified_by', 'verified', 'admin_tags']
        admin_skip_data = dict(map(lambda key: (key, posted_data.get(key, None)), admin_skip_keys))
        admin_skip_data['dirty_by_admin'] = True
        db.products.update({'_id': ObjectId(id)}, {"$set": admin_skip_data})
    
    else:
        print('####id####data to be saved -- verified --####', id, posted_data)
        db.products.update({'_id': ObjectId(id)}, {"$set": posted_data})
        inc_tag_count(user_id, True)

    #fetching next product tagging info
    if q == 'verify':
        tagging_info = get_product_tagging_details(next_name, True)
    elif q == '3-skips':
        tagging_info = get_product_tagging_details(next_name, False, True)

    if undo:
        db.products.update({'_id': ObjectId(id)},{"$unset":{'admin_tags':'','verified_by':'','verified':'','dirty_by_admin':''}})
        dcr_tag_count(user_id, True)

    tag_count, verify_count = get_tag_count(user_id)
    tagging_info['tag_count'] = tag_count
    tagging_info['verify_count'] = verify_count
    print('----------------------------------------------',tagging_info)
    return json.dumps(tagging_info)

@bp.route('/add-subcat', methods=['GET', 'POST'])
def add_subcat():
    if 'user' in session and session['is_admin']:
        subcat_status = 'Not Added'
        if request.form:
            if len(request.form['subcat']) and request.form['category'] != '-1':
                subcat_status = add_new_subcat( request.form['category'], request.form['subcat'] )
            else:
                subcat_status = 'Error'
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        return render_template("add_sub_cat.html",
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count,
                               available_cats=get_categories(),
                               subcat_status=subcat_status)
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('bp.login'))

@bp.route('/leaderboard')
def view_leaderboard():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        return render_template("leaderboard.html",
                               users=get_users(),
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count)
    else:
        return redirect(url_for('bp.login'))

@bp.route('/tag-list')
def get_tags():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        return render_template("tag_list.html",
                               tags=get_all_tags(),
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count)
    else:
        return redirect(url_for('bp.login'))


app.register_blueprint(bp, url_prefix='/cat-ui')
if __name__ == '__main__':
    app.debug = True
    app.run()
