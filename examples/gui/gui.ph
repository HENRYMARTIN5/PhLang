func onButtonClick()
    window_create_button("Close window", 0, 100, "exit()")
end


func main()
    openwindow("Hello, World!", "#ffffff")
    window_create_button("Add new button", 0, 50, "onButtonClick()")
    window_create_text("Hello, World!", 0, 0)
end

main()