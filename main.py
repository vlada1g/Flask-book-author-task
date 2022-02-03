from api import app,db     

# migrate = Migrate(app, db)

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True,host='0.0.0.0')