

## import 
 in `~/.lldbinit`
```
command script import /<PATH>/cclet.py
command script import /<PATH>/preturn.py
command script import /<PATH>/enum_open.py
```


# custom_commands
## vinfo.py
### 概要
 * 現在表示されているUIKitのコンポーネントにデバッグコンソール上で簡単にアクセスできる。
 
### USAGE
 * consoleに`vinfo`を入力
 * View Hierarchyから任意のコンポーネントをコンソールにドラッグして使用
 
```
(lldb) vinfo ((UIViewController *)0x7f99a3823c00)  // ドラッグするとこの形で自動的に入力される。
type lookup MewExample.MainViewController   // 型情報。
　　　　　　　　　　　　　　　　　　　　　　　　　　 // この行をコピーしてconsole上で実行すると型のもつメンバ➖も確認できる。
Use in swift context　 　　　　　　　　　　　　　// アクセス可能な言語コンテキストを表示
$R170   　　　　　　　　　　　　　　　　　　　　　　// コンソールで使用できる変数

(lldb) po $R170.view  
▿ Optional<UIView>   
  - some : <UIView: 0x7f99a3506d30; frame = (0 0; 375 667);    autoresize = W+H; layer = <CALayer: 0x60000240aec0>>    
```

## enum_open.py
 * Enumの付属値を取得する。
	* 付属値が２つ以上の場合 Tupleとして取得できる。
```
(lldb) enum_open <enum with attValue>
```

## preturn.py
* メソッドの返り値の型がレジスタに格納できる値の場合に、任意の値にすることができる。ブレークポイントをONにしておく必要がある。
<img width="1173" alt="screen shot 2018-09-02 at 9 53 18" src="https://user-images.githubusercontent.com/14083051/44951112-28f0d780-ae96-11e8-860d-0f0b844785e2.png">


## cclet.py
 * Xcode10からStringの構造が変わったため使用不可
	 * SwiftClassのletで定義された、任意のString型のメンバーの文字列を変更できる

```
(lldb) <instanceName>.<targetLetMember> = "hogehoge"
// ex) hogeInstance.str = "hogehoge"
```

# etc
* Xcode9.4.1にて動作確認しました。
* プロトタイプなのでバグがあります。使用は自己責任でお願いします。m(_ _)m
