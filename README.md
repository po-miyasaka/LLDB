

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
### 概要
 * コンソール上で簡単にenumの付属値を取り出す。
	* 付属値が２つ以上の場合 Tupleとして取得できる。
	
### USAGE  
 *  `enum_open` コマンドに enumの変数を渡す。
	* インスタンスのメンバーの場合はself.をつける。
	* Optional型の場合は強制アンラップする必要がある。  
	
```
(lldb) enum_open self.hogeEnum!
Example.MainViewController.Testes.hogeEnum
((MewExample.EnvironmentMock, (), Swift.String)) // 型情報
$R140 // コンソールで使える変数

(lldb) po $R140
▿ 3 elements
  - .0 : <EnvironmentMock: 0x600002645fa0>
  - .1 : 0 elements
  - .2 : "aaaaaaa"

(lldb) po $R140.2
"aaaaaaa"
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
