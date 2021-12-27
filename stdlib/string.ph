var private_string_ascii = "翿翿翿翿翿翿翿翿翿\t\n翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿翿 !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~翿"

func string_concat(str, suffix)
  return str + suffix
end

func string_charAt(str, idx)
  return str / idx
end

func string_charCodeAt(str, idx)
  var char = string_charAt(str, idx)

  for i = 0 to len(private_string_ascii) then
    if char == private_string_ascii/i then
      return i
    end
  end

  return -1
end

func string_split(str)
  var list = []

  for i = 0 to len(str) then
    APPend(list, str/i)
  end

  return list
end

func string_indexOf(str, char)
  for i = 0 to len(str) then
    if str/i == char then
      return i
    end
  end

  return -1
end

func string_lastIndexOf(str, char)
  for i = len(str)-1 to -1 STEP -1 then
    if str/i == char then
      return i
    end
  end

  return -1
end

print("Loaded stdlib library string.ph"); return 0