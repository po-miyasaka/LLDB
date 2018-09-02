

## import 
 in `~/.lldbinit`
```
command script import /<PATH>/cclet.py
command script import /<PATH>/preturn.py
command script import /<PATH>/enum_open.py
```


# USAGE
## cclet.py
 * SwiftClassのletで定義された、任意のString型のメンバーの文字列を変更できる
```
(lldb) <instanceName>.<targetLetMember> = "hogehoge"
```

## enum.py
 * Enumの付属値を取得する。
 * タプルのように付属値の番号を指定する必要がある。
```
(lldb) enum_open <enum With AttValue>.0
```

## preturn.py
* メソッドの返り値の型がレジスタに格納できる値の場合に、任意の値にすることができる。ブレークポイントをONにしておく必要がある。
<img width="1173" alt="screen shot 2018-09-02 at 9 53 18" src="https://user-images.githubusercontent.com/14083051/44951112-28f0d780-ae96-11e8-860d-0f0b844785e2.png">

# etc
* Xcode9.4.1にて動作確認しました。
* プロトタイプなのでバグがあります。使用は自己責任でお願いします。m(_ _)m
