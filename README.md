#  概要
インスタンスのアドレスからデバッグ用変数を作るLLDBコマンド `vinfo`を実装した。  
`Memory Graph` や `View Hierarchy`からインスタンスのアドレスをコピーして使用することができる。  

# セットアップ方法
`~/.lldbinit`ファイルに以下のように記載して保存する。

```
command script import ~/<任意のPATH>/vinfo.py
```  

# 基本的な使用例
#### アドレスからデバッグ用の変数を生成
```
(lldb) vinfo 0x7f99a3823c00
For Swift                         // アクセス可能な言語コンテキストを表示
type lookup Sample.ViewController // 型情報
$R170   　　　　　　　　　　　　　　　  // コンソールで使用できる変数

(lldb) po $R170.view  
▿ Optional<UIView>   
  - some : <UIView: 0x7f99a3506d30; frame = (0 0; 375 667);    autoresize = W+H; layer = <CALayer: 0x60000240aec0>>    
```

# 備考
## コマンド引数について
`(lldb) vinfo ((id)0x7fdf73d1c050)`のような形で入力しても動作する。  
この形式は以下のような操作で自動的に入力される。   

* `View Hierarchy`もしくは`Memory Graph`のDebugNavigatorからコンポーネントをコンソールにドラッグする  
* `View Hierarchy`もしくは`Memory Graph`のDebugNavigatorからコンポーネントにフォーカスをあてた状態で⌘ + Cを入力後コンソールにペーストする  
* `ViewHierarchy`のビジュアル画面でコンポーネントを選んだ状態で⌘ + Cを入力後コンソールにペーストする  
* `Memory Graph`のNodeを選んだ状態で⌘ + Cを入力後コンソールにペーストする  

## type lookupについて
`type lookup HOGE` はメンバ一覧を表示するLLDBコマンド  
`type lookup NSObject`と　  
`type lookup NSObject `では出力結果が違うので注意  (末尾の半角スペースの有無の違い)

## `pos` `poc`などのコマンドエイリアスについて
 `vinfo`をインポートすると `pos`や  `poc`のようなコマンドが使えるようになる   
以下のようにすることでブレーク時のフレームの言語設定に左右されずに各言語のコードが使用できる。   
* Swiftのコードを実行する場合は`po`の代わりに`pos`を使用  
* ObjC のコードを実行する場合は`po`の代わりに`poc`を使用  



## 動作環境
`XCode10.0`以上
