func onButtonClick()
    print("ButtonClick!")
end


func main()
    openwindow("Hello, World!", "#ffffff")
    window_create_button("Test", 0, 0, "onButtonClick()")
end
