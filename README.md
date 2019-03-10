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
For Swift					// アクセス可能な言語コンテキストを表示
type lookup MewExample.MainViewController   	// 型情報。この行をそのままコピーしてコンソール上で実行すると型のもつメンバ➖も確認できる　　　　　　　　　　　　
$R170   　　　　　　　　　　　　　　　　　　　　　　// コンソールで使用できる変数

(lldb) po $R170.view  
▿ Optional<UIView>   
  - some : <UIView: 0x7f99a3506d30; frame = (0 0; 375 667);    autoresize = W+H; layer = <CALayer: 0x60000240aec0>>    
```

#### Swiftの変数として出力する例
```
(lldb) vinfo ((UIView *)0x7fc140713220) // UIKitライブラリに実装されたコンポーネントはデフォルトでObjective-Cの変数として出力される
For Objc
type lookup UIView
$82

(lldb) vinfo -s ((UIView *)0x7fc140713220)//  -sコマンドを使うことでSwiftの変数として出力される
For Swift
type lookup UIView
$R84
```
