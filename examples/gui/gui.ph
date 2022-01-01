func onButtonClick()
    exit()
end


func main()
    openwindow("Hello, World!", "#ffffff")
    window_create_button("Close window", 0, 0, "onButtonClick()")
end

main()

