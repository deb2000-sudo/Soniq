#import an object:"Flask",method:"render_template" from module flask
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from model import *
import datetime
# from datetime import timedelta,datetime
from flask_login import LoginManager,login_user,logout_user,current_user,UserMixin,login_required
from werkzeug.security import check_password_hash,generate_password_hash
# from flask_wtf import FlaskForm
# from wtforms import FloatField
#name of app does not matter creation of app variable app will be inherit function and other things from Flask 
app=Flask(__name__)

#database connection to sqlite
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///musicplayer.sqlite3'
app.config['SECRET_KEY']='mysecretkey'


db.init_app(app)
login_manager=LoginManager(app)

app.app_context().push()

#this function act like session the user object load in to session
@login_manager.user_loader
def load_user(user_id):
    if "_" in user_id:
        user_type, user_id = user_id.split("_")
    else:
        user_type = "user"

    if user_type == "user":
        return Userinfo.query.get(user_id)
    elif user_type == "admin":
        return Adminauth.query.get(user_id)
    

#creation of routes using app varibale

#use of decorator 
#route is a method/function for mapping a web page
@app.route('/',methods=['GET','POST'])
def landing_page():
    return render_template('index.html')

#End point for Normal user and creator Login in app
@app.route('/login',methods=['GET','POST'])
def user_login_page():
    #when POST HTTP method is implemented
    if request.method=='POST':
        #Take username from login page by name attribute
        f_username=request.form.get('username')
        #Take password from login page by name attribute
        f_password=request.form.get('password')
        #Check if user name is present or not in database
        this_user=Userinfo.query.filter(Userinfo.Username==f_username).first() #query filter return a query object first method take the first row so this_user is the object
        #print(this_user.id)
        #when user is not logged in
        loggedin=False
        if this_user:
            if check_password_hash(this_user.Password,f_password):
                #login succesful!! when user is logged in 
                loggedin=True
                #flask login to know login happened and save it to session save is done by login_user
                login_user(this_user)
                #check whether user is a normal user or a creator or an admin
                if this_user.Normaluser==True and this_user.Creator==False:
                    #if a user is not a creator
                    flash('You are successfully logged in')
                    profile='normal-user'
                    return redirect(url_for('dashboard',profile=profile))
                elif(this_user.Normaluser==True and this_user.Creator==True):
                    #if a user is a creator
                    profile='normal-user'
                    return redirect(url_for('dashboard',profile=profile))
                else:
                    pass
            else:
                return render_template('login.html',loggedin=loggedin)
        else:
            return render_template("login.html",loggedin=loggedin)
    return render_template('login.html')



@app.route('/dashboard/<string:profile>',methods=['GET','POST'])
@login_required
def dashboard(profile):
    #checking whether login is made by administrator
    # print(1)
    if profile=='admin':
        this_admin=Adminauth.query.get(current_user.id)
        Normal_user_count=Userinfo.query.filter_by(Normaluser=True).count()
        Creator_count=Userinfo.query.filter_by(Creator=True).count()
        Total_songs_count=Songs.query.count()
        all_genre_count=Songs.query.with_entities(Songs.Genre.distinct()).count()
        Total_Album_count=Album.query.count()
        return render_template('dashboard.html',profile=profile,this_admin=this_admin,Normal_user_count=Normal_user_count,Creator_count=Creator_count,Total_songs_count=Total_songs_count,all_genre_count=all_genre_count,Total_Album_count=Total_Album_count)
    # print(2)
    #initially when a user will login based on role, role can be normal-user or creator
    currentrole=profile
    switch_status=False
    switch_value="Switch to Creator"
    this_user=Userinfo.query.get(current_user.id)
    #initially it will show 
    if request.method=='POST' and switch_value==request.form.get('switch'):
        # print(1)
        switch_status=True
        switch_value="Switch to User"
        currentrole="creator"
        this_user_song=Songs.query.filter(Songs.user_id==current_user.id)
        this_user_album=Album.query.filter(Album.user_id==current_user.id)
        avg_rating = db.session.query(func.avg(Rating.rating_value)).\
        join(Songs, (Rating.song_id == Songs.id) & (Songs.user_id == this_user.id)).\
        scalar()
        Scount=Songs.query.filter(Songs.user_id==current_user.id).count()
        Acount=Album.query.filter(Album.user_id==current_user.id).count()
        all_albums=Album.query.filter(Album.user_id==this_user.id).all()
        return render_template('dashboard.html',user=this_user,this_user_song=this_user_song,switch_status=switch_status,switch_value=switch_value,Scount=Scount,Acount=Acount,profile=currentrole,this_user_album=this_user_album,avg_rating=avg_rating,all_albums=all_albums)
    else:
      #initially it will show by GET method
      switch_status=False
      switch_value="Switch to Creator"
      all_songs=Songs.query.all()
      playlist_this_user=Playlist.query.filter(Playlist.user_id==current_user.id)
    #   print(all_songs)
    #   print(playlist_this_user)
      all_genre=Songs.query.with_entities(Songs.Genre.distinct()).all()
      all_albums=Album.query.filter(Album.user_id==this_user.id).all()
      print(all_albums)
      return render_template('dashboard.html',user=this_user,all_songs=all_songs,switch_status=switch_status,switch_value=switch_value,profile=currentrole,playlist_this_user=playlist_this_user,all_genre=all_genre,all_albums=all_albums)
    
@app.route('/dashboard/<int:id>/read-lyrics/<int:S_id>',methods=['GET','POST'])
@login_required
def read_lyrics(id,S_id):
    this_user=Userinfo.query.get(id)
    Require_song=Songs.query.filter(Songs.id==S_id).first()
    Creator=Userinfo.query.filter(Userinfo.id==Require_song.user_id).first()
    if request.method=='POST':
        # print(1)
        rating_added=False
        rating_of_song=request.form.get('rating')
        rating=int(rating_of_song)
        # print(rating)
        #this use and this song
        this_user=Userinfo.query.get(id)
        Require_song=Songs.query.filter(Songs.id==S_id).first()
        #Check existing rating present
        already_rated=Rating.query.filter(Rating.user_id==this_user.id,Rating.song_id==Require_song.id).first()
        # print(already_rated)

        if already_rated:
            already_rated.rating_value=rating
        else:
            # print(2)
            rating_to_add=Rating(rating_value=rating,user_id=id,song_id=S_id)
            db.session.add(rating_to_add)
            db.session.commit()
            rating_added=True
        return render_template('show_songs.html',user=this_user,Require_song=Require_song,Creator=Creator,rating_added=rating_added)
    else:
        # this_user=Userinfo.query.get(id)
        # Require_song=Songs.query.filter(Songs.id==S_id).first()
        # Creator=Userinfo.query.filter(Userinfo.id==Require_song.user_id).first()
        return render_template('show_songs.html',user=this_user,Require_song=Require_song,Creator=Creator)


    #Handling the GET Case
    #fetch the user
    
@app.route('/dashboard/<int:id>/update_song/<int:S_id>',methods=['GET','POST','PUT'])
def update_song(id,S_id):
    if request.method=="POST":
        #first find song object that needs to update
        song_updated=False
        song_require_update=Songs.query.filter(Songs.id==S_id).first()

        #fetchthe input dtata 
        current_s_name=request.form.get("title")
        current_s_lyrics=request.form.get("lyrics")
        current_s_duration=request.form.get("duration")
        current_s_artist=request.form.get("singer")
        current_s_date=request.form.get("release_date")
        current_release_date = datetime.date.fromisoformat(current_s_date)
        current_s_genre=request.form.get("genre")
        #update the data

        song_require_update.Name=current_s_name
        song_require_update.Lyrics=current_s_lyrics
        song_require_update.Duration=current_s_duration
        song_require_update.Artist=current_s_artist
        song_require_update.Date_created=current_release_date
        song_require_update.Genre=current_s_genre

        db.session.commit()
        song_updated=True
        # print(1)
        profile="creator"
        return redirect(url_for('dashboard',profile=profile))
    else:
        #GEt method it should fill all the form details
       song_needs_toUpdated=Songs.query.filter(Songs.id==S_id).first()
       title= song_needs_toUpdated.Name
       lyrics=song_needs_toUpdated.Lyrics
       print(lyrics)
       duration=song_needs_toUpdated.Duration
       artist=song_needs_toUpdated.Artist
       date_creation=song_needs_toUpdated.Date_created
       genre=song_needs_toUpdated.Genre
       return render_template('update_song.html',title=title,lyrics=lyrics,duration=duration,artist=artist,date_creation=date_creation,genre=genre,S_id=S_id,id=id)

@app.route('/dashboard/<string:profile>/update-playlist/<int:P_id>',methods=['GET','POST','PUT'])
def update_playlist(profile,P_id):
    if request.method=="POST":
        return redirect(url_for("dashboard"))
    else:
        #GEt method it should fill all the form details
       playlistneeds_toUpdated=Playlist.query.filter(Playlist.id==P_id).first()
       playlistname= playlistneeds_toUpdated.Name
       All_songs=playlistneeds_toUpdated.songs
       return render_template('update_playlist.html',playlistname=playlistname,All_songs=All_songs,profile=profile,P_id=P_id)
#update Album
@app.route('/dashboard/<string:profile>/update-album/<int:A_id>',methods=['GET','POST','PUT'])
def update_album(profile,A_id):
    if request.method=="POST":
        return redirect(url_for("dashboard"))
    else:
        #GEt method it should fill all the form details
       albumneeds_toUpdated=Album.query.filter(Album.id==A_id).first()
       Albumname= albumneeds_toUpdated.Name
       Albumgenre=albumneeds_toUpdated.Genre
       Albumartist=albumneeds_toUpdated.Artist
    #    All_songs=albumneeds_toUpdated.songs
       return render_template('update_Album.html',Albumname=Albumname,profile=profile,P_id=A_id,Albumgenre=Albumgenre,Albumartist=Albumartist)

#Delete song
@app.route('/dashboard/<int:id>/delete_song/<int:S_id>',methods=['GET','PATCH','POST'])
def delete_song(id,S_id):
    song_need_todelete=Songs.query.filter(Songs.id==S_id).first()

    
    associated_ratings = Rating.query.filter_by(song_id=S_id).all()
    db.session.delete(song_need_todelete)
    for rating in associated_ratings:
        db.session.delete(rating)
        
    db.session.commit()
    profile='creator'
    return redirect(url_for('dashboard',profile=profile))
    


    
@app.route('/dashboard/<string:profile>/upload_song',methods=['GET','POST','PUT'])
#to get creator form there is a need of login required
@login_required
def be_creator(profile):
    #fetch the user object which have logged in
    this_user=Userinfo.query.get(current_user.id)
    if request.method=='POST':
        song_added=False
        #take the data to upload a song from form
        title=request.form.get('title')
        singer=request.form.get('singer')
        duration=request.form.get('duration')
        genre=request.form.get('genre')
        release_date=request.form.get('release_date')
        lyrics=request.form.get('lyrics')
        release_date = datetime.date.fromisoformat(release_date)
        #creation of song object
        song_to_add=Songs(Name=title,Artist=singer,Lyrics=lyrics,Duration=duration,Date_created=release_date,Genre=genre,user_id=current_user.id)
        #song object add to database
        db.session.add(song_to_add)
        #commit on database
        db.session.commit()
        #mark as song added succesfully on database
        song_added=True
        if song_added:
            this_user.Creator=True
            db.session.commit()
            return redirect(url_for('creator',profile=profile))
        else:
            pass
    else:
        return render_template('creator-form.html',user=this_user,profile=profile)

@app.route('/dashboard/<string:profile>')
@login_required
def creator(profile):
    #we have to conver string into boolean
    song_added=song_added.lower()=='true'
    this_user=Userinfo.query.get(current_user.id)
    #make the change in database user became creator
    this_user.Creator=True
    db.session.commit()
    # print(this_user)
    profile="creator"
    return render_template('dashboard.html',user=this_user,song_added=song_added,id=id,profile=profile)


category_data={}
@app.route('/dashboard/<string:profile>/create_album',methods=['GET','POST'])
@login_required
def create_album(profile):
    this_user=Userinfo.query.get(current_user.id)
    # print(this_user)
    if request.method=='POST' and profile=='creator':
        # print(type(option_choosed))
        #there is three form here
        #for form 1
        if 'category' in request.form:
            #fetch data from form
            option=request.form.get('category')
            result1=[]
            if option=='genre':
                category_data['option_choosed_in_form_1']='genre'
                #print(2,option,option_choosed)
                #List of song object group by Genre where user id is current user id
                Qresult=Songs.query.filter(Songs.user_id == this_user.id).group_by(Songs.Genre).all()
                for item in Qresult:
                    result1.append(item.Genre)
                # print(result1)
            else:
                category_data['option_choosed_in_form_1']='artist'
                Qresult=Songs.query.filter(Songs.user_id == this_user.id).group_by(Songs.Artist).all()
                for item in Qresult:
                    result1.append(item.Artist)
                # print(result1)
            return render_template('create_album.html',user=this_user,result1=result1,category_data=category_data,profile=profile)
        #for form 2 
        if 'results' in request.form:
            #fetch data  from form 2
            # print('in  2nd form')
            result2=[]
            Scategory=request.form.get('Scategory')
            # print(Scategory)
            if category_data['option_choosed_in_form_1']=='genre':
                Qresults = Songs.query.filter(Songs.user_id == this_user.id, Songs.Genre == Scategory).all()
            elif category_data['option_choosed_in_form_1']=='artist':
                Qresults = Songs.query.filter(Songs.user_id == this_user.id, Songs.Artist == Scategory).all()
            #print(Qresults)
            for item in Qresults:
                result2.append((item.id,item.Name))
            print(result2)
            return render_template('create_album.html',user=this_user,result2=result2,category_data=category_data,profile=profile)
        #for form 3
        if 'submit' in request.form:
            album_added=False
            album_name=request.form.get('album_name')
            album_category=request.form.get('album_category')
            #create a album object
            print(album_name,"     ",album_category,'checing1')
            if category_data['option_choosed_in_form_1']=='genre':
                album_to_add=Album(Name=album_name,Genre=album_category,user_id=current_user.id)
                db.session.add(album_to_add)
                db.session.commit()
                album_added=True
                print(album_added)
            elif category_data['option_choosed_in_form_1']=='artist':
                album_to_add=Album(Name=album_name,Artist=album_category,user_id=current_user.id)
                db.session.add(album_to_add)
                db.session.commit()
                album_added=True
                print(album_added)
            #update the song database
            #get the album id
            album_t=Album.query.filter(Album.Name==album_name).first()
            # print(album_t,'checking')
            album_id=album_t.id
            print(album_id,"album_id")
            song_updated=False
            #get tha all song selected
            song_id_selected=request.form.getlist("song_selected")
            print("checking_song_id",song_id_selected)
            for song_id in song_id_selected:
                #first fetch the song from song table
                print(song_id,'song_id',type(song_id))
                s_id=int(song_id)
                print(s_id,'s_id',type(s_id))
                l_to_update_song= Songs.query.filter(Songs.id == s_id).first()
                l_to_update_song.album_id=album_id
                db.session.commit()
                song_updated=True
            return redirect(url_for('creator',id=this_user.id,song_updated=song_updated,album_added=album_added,profile=profile))
    else:
        #for GET request it is rendered first
        return render_template('create_album.html',user=this_user,category_data=category_data,profile=profile)

@app.route('/dashboard/<string:profile>/create_playlist',methods=['GET','POST'])
@login_required
def create_playlist(profile):
    this_user=Userinfo.query.get(current_user.id)
    #for a post method or form submission
    if request.method=='POST' and profile=='normal-user':
        playlist_name=request.form.get('playlist_name')
        playlist_to_add=Playlist(Name=playlist_name,user_id=current_user.id)
        db.session.add(playlist_to_add)
        db.session.commit()
        print(playlist_to_add)
        song_id_selected=request.form.getlist("song_selected")
        # for song_id in song_id_selected:
        #     Song_association_playlist
        song_id_selected=request.form.getlist("song_selected")
        for song_id in song_id_selected:
            data_to_add=Song_association_playlist(song_id=song_id,playlist_id=playlist_to_add.id)
            db.session.add(data_to_add)
            db.session.commit()
        return redirect(url_for('dashboard',profile=profile))
        
        return render_template('dashboard.html',profile=profile,user=this_user)
    #fetch all songs available to this user to make a playlist
    all_songs=Songs.query.all()
    return render_template('create_playlist.html',profile=profile,all_songs=all_songs)

@app.route('/dashboard/<string:profile>/playlist/<int:playlist_id>/songs',methods=['GET','POST'])
def get_song_playlist(profile,playlist_id):
    playlist=Playlist.query.filter(Playlist.id==playlist_id).first()
    All_songs=playlist.songs
    # print(All_songs)
    return render_template('view_playlist_songs.html',profile=profile,All_songs=All_songs,playlist=playlist)

@app.route('/user_profile')
@login_required
def user_detail():
    this_user=Userinfo.query.get(current_user.id)
    print(this_user)
    return render_template('user_profile.html',user=this_user)

@app.route('/user_logout')
@login_required
def user_logout():
    logout_user()
    return redirect('/')

@app.route('/admin_register',methods=['GET','POST'])
def admin_register():
    if request.method=='POST':
        #take the username from form to check whether username already taken or not
        f_admin_username=request.form.get('username')
        #check whether the username provided by the user is already present in database or not
        this_admin=Adminauth.query.filter(Adminauth.admin_user_name==f_admin_username).first()
        this_admin_present=False
        if this_admin==None:
            admin_added=False
            #if there is no admin of this username then we will register the admin
            #here only password is required
            f_password=request.form.get('password')
            #creation of admin object
            admin_to_add=Adminauth(admin_user_name=f_admin_username,admin_password=generate_password_hash(f_password))
            #admin object add to database
            db.session.add(admin_to_add)
            #commit on database
            db.session.commit()
            admin_added=True
            return render_template("admin_login.html",admin_added=admin_added)
        else:
            this_admin_present=True
            return render_template("admin_register.html",this_admin_present=this_admin_present)
    else:
        #when the client wants a resource where http method is GET
        return render_template('admin_register.html')

#End point for Administrator Login in app
@app.route('/admin_login',methods=['GET','POST'])
def admin_login_page():
    #when POST HTTP method is implemented
    print(1)
    if request.method=='POST':
        #Take usernmae from admin login page by name attribute
        a_f_username=request.form.get('username')
        #Take password from admin login page by name attribute
        a_f_password=request.form.get('password')
        #check username is present is database or not 
        this_admin=Adminauth.query.filter(Adminauth.admin_user_name==a_f_username).first()
        #when admin is not logged in
        loggedin=False
        if this_admin:
            if check_password_hash(this_admin.admin_password,a_f_password):
                #admin logged in succesful
                loggedin=True
                login_user(this_admin)
                profile='admin'
                return redirect(url_for('dashboard',profile=profile))
            else:
                return render_template('admin_login.html',loggedin=loggedin)
        else:
            return render_template('admin_login.html',loggedin=loggedin)
    return render_template('admin_login.html')

@app.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return redirect('/')


@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        #take the username from form to check whether username already taken or not
        f_username=request.form.get('username')
        #check whether the username provided by the user is already present in database or not
        this_user=Userinfo.query.filter(Userinfo.Username==f_username).first()
        this_user_present=False
        if this_user==None:
            user_added=False
            #if there is no user of this username then we will register by taking form data
            fname=request.form.get('fname')
            lname=request.form.get('lname')
            password=request.form.get('password')
            phone_no=request.form.get('mobno')
            #creation of user object
            user_to_add=Userinfo(Username=f_username,First_name=fname,Last_name=lname,Password=generate_password_hash(password),Mobile_no=phone_no)
            #user object add to database
            db.session.add(user_to_add)
            #commit on database
            db.session.commit()
            #mark as user added succesfully on database
            user_added=True
            return render_template("login.html",user_added=user_added)
        else:
            this_user_present=True
            return render_template("user_registration.html",this_user_present=this_user_present)
    else:
        #when the client needs a resource method is GET
        return render_template('user_registration.html')

app.run(debug=True)
