# 概要
アプリ開発やデバッグ作業で使えそうなLLDBコマンドをまとめる。　　
複数のコマンドを一つのファイル (`pm_lldb_commands.py`)に実装している

# インポート方法
`~/.lldbinit`ファイルを用意して以下を記載する
デバッグ時に各種コマンドが使えるようになる(PATH部分は任意)

```
command script import /<PATH>/pm_lldb_commands.py
```

# 各種コマンドについて
## `vinfo`
### 概要
メモリ上にあるUIクラスやデータクラスを、デバッグコンソール上で簡単に変数化できる
 
### 使い方
#### UIコンポーネントを変数として出力
1. consoleに`vinfo`を入力
2. View Hierarchyの左サイドバーから任意のコンポーネントをコンソールにドラッグして実行

#### Memory Graphから任意のクラスを変数として出力
1. consoleに`vinfo`を入力
2. MemoryGraghの左サイドバーから任意のコンポーネントの**アドレス**をコンソールにドラッグして実行
  
#### 基本的な使用例
```
(lldb) vinfo ((UIViewController *)0x7f99a3823c00)  // ドラッグするとこの形で自動的に入力される。
type lookup MewExample.MainViewController   // 型情報。この行をそのままコピーしてコンソール上で実行すると型のもつメンバ➖も確認できる
Use in swift context　 　　　　　　　　　　　　　// アクセス可能な言語コンテキストを表示
$R170   　　　　　　　　　　　　　　　　　　　　　　// コンソールで使用できる変数

(lldb) po $R170.view  
▿ Optional<UIView>   
  - some : <UIView: 0x7f99a3506d30; frame = (0 0; 375 667);    autoresize = W+H; layer = <CALayer: 0x60000240aec0>>    
```

#### Swiftの変数として出力する例
```
(lldb) vinfo ((UIView *)0x7fc140713220) // UIKitライブラリに実装されたコンポーネントはデフォルトでObjective-Cの変数として出力される
type lookup UIView
Use in objc context
$82

(lldb) vinfo -s ((UIView *)0x7fc140713220)//  -sコマンドを使うことでSwiftの変数として出力される
type lookup UIView
UIView
Use in swift context
$R84
```


## `enum_open`
### 概要
 * コンソール上で簡単にenumの付属値を取り出す。
	* 付属値が２つ以上の場合 Tupleとして取得できる。
	
### 使い方
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


## `cbd`
### 概要
* current breakpoint (disable | delete)の略
*  ブレークした時に実行すると、ブレークした原因となるBreakPointを無効にする
### 使い方
* Options
	* -d
		* BreakPointを削除する 
	* -c
		* 実行後にプロセスを再開する。


## `preturn`
* メソッドの返り値の型がレジスタに格納できる値の場合に、任意の値にすることができる。ブレークポイントをONにしておく必要がある。
<img width="1173" alt="screen shot 2018-09-02 at 9 53 18" src="https://user-images.githubusercontent.com/14083051/44951112-28f0d780-ae96-11e8-860d-0f0b844785e2.png">


## `cclet`
 * Xcode10からStringの構造が変わったため使用不可
	 * SwiftClassのletで定義された、任意のString型のメンバーの文字列を変更できる

```
(lldb) hogeInstance.str = "hogehoge"
(lldb) hogeInstantce.str
"hogehoge"
```
