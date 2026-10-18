#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
質問の読み上げ音声（VOICEVOX）を、questions.js からまとめて作るスクリプトです。

【使い方】
 1. VOICEVOX（アプリ）を起動したままにします。
 2. このフォルダで、次のように実行します。
      python make_audio.py              ← 標準の声（話者ID 11）で作成
      python make_audio.py --list       ← 使える声の一覧（話者IDの確認）
      python make_audio.py --speaker 13 ← 声を変えて作成
      python make_audio.py --force      ← 作成ずみの音声も作り直す
 3. audio フォルダ（音声ファイルと manifest.js）ができます。
    index.html と同じ場所に置いて公開してください。

【注意】
 ・Python 3 だけで動きます（追加のインストールは不要です）。
 ・VOICEVOX の利用規約、および選んだキャラクターごとの利用規約をご確認ください。
   公開するときは、クレジット表記（「VOICEVOX:キャラクター名」）が必要です。
   表記は manifest.js に自動で入り、ページの下に表示されます。
 ・問題を追加・修正したら、もう一度実行してください（新しい問題だけ作成されます。
   文言を直した問題は --force で作り直します）。
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request, urllib.error

def load_sets(path):
    txt = open(path, encoding='utf-8').read()
    m = re.search(r'^window\.QUESTION_SETS\s*=\s*', txt, re.M)
    body = txt[m.end():].strip()
    if body.endswith(';'):
        body = body[:-1]
    return json.loads(body)

def http(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def reading_text(q, mapping):
    t = q.get('read') or q['q']
    for k, v in (mapping or {}).items():
        t = t.replace(k, v)
    return t

def find_credit(host, speaker):
    try:
        sp = json.loads(http('GET', host + '/speakers').decode('utf-8'))
        for s in sp:
            for st in s.get('styles', []):
                if st.get('id') == speaker:
                    return 'VOICEVOX:' + s['name']
    except Exception:
        pass
    return 'VOICEVOX'

def main():
    ap = argparse.ArgumentParser(description='VOICEVOXで質問の読み上げ音声を作ります')
    ap.add_argument('--host', default='http://127.0.0.1:50021', help='VOICEVOXエンジンのアドレス')
    ap.add_argument('--speaker', type=int, default=11, help='話者ID（--list で確認）')
    ap.add_argument('--speed', type=float, default=0.95, help='話す速さ（1.0が標準）')
    ap.add_argument('--questions', default='questions.js')
    ap.add_argument('--out', default='audio')
    ap.add_argument('--force', action='store_true', help='作成ずみの音声も作り直す')
    ap.add_argument('--list', action='store_true', help='使える声の一覧を表示')
    a = ap.parse_args()

    try:
        http('GET', a.host + '/version')
    except Exception as e:
        print('VOICEVOXに接続できません。VOICEVOXを起動してから、もう一度実行してください。')
        print('(', e, ')')
        sys.exit(1)

    if a.list:
        for s in json.loads(http('GET', a.host + '/speakers').decode('utf-8')):
            print(s['name'])
            for st in s.get('styles', []):
                print('   話者ID %-4d %s' % (st['id'], st['name']))
        return

    sets = load_sets(a.questions)
    credit = find_credit(a.host, a.speaker)
    ids = {}
    made = skipped = 0
    for st in sets:
        d = os.path.join(a.out, st['id'])
        os.makedirs(d, exist_ok=True)
        ids[st['id']] = []
        for q in st['questions']:
            fn = os.path.join(d, q['id'] + '.wav')
            ids[st['id']].append(q['id'])
            if os.path.exists(fn) and not a.force:
                skipped += 1
                continue
            text = reading_text(q, st.get('reading'))
            qs = urllib.parse.urlencode({'text': text, 'speaker': a.speaker})
            query = json.loads(http('POST', a.host + '/audio_query?' + qs).decode('utf-8'))
            query['speedScale'] = a.speed
            query['prePhonemeLength'] = 0.3
            query['postPhonemeLength'] = 0.4
            wav = http('POST', a.host + '/synthesis?speaker=%d' % a.speaker,
                       data=json.dumps(query).encode('utf-8'),
                       headers={'Content-Type': 'application/json'})
            open(fn, 'wb').write(wav)
            made += 1
            print('作成:', fn, '←', text[:30])

    manifest = {'credit': credit, 'ext': 'wav', 'ids': ids}
    with open(os.path.join(a.out, 'manifest.js'), 'w', encoding='utf-8') as f:
        f.write('window.AUDIO_MANIFEST = ' + json.dumps(manifest, ensure_ascii=False) + ';\n')
    print('完了：新しく%d件、作成ずみ%d件。クレジット表記：%s' % (made, skipped, credit))

if __name__ == '__main__':
    main()
