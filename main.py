from website import create_app

app = create_app()

if __name__=='__main__': #run web server if we run, not imported
    app.run(debug=True)

    