# Downloading Manwha

## Step 1: Download

```shell
SRC_URL="https://comix.to/title/3nyv-for-my-derelict-favorite"
NAME="For My Derelict Favorite"

cd /home/shalom/workspace/download-manwha/derelict-favorite/v3/comix-downloader
source venv/bin/activate
python main.py download "$SRC_URL" -c "1-10"
```

## Step 2: Check for missing

```shell
python3 /home/shalom/workspace/download-manwha/generate-manhwa-html/check_missing_chapters.py "downloads/$NAME"
```

If any are missing, go back to step 1 to retry

## Step 2.5: Rename 1-digit and 2-digit chapter folders to be 3-digit

```shell
pushd .
cd "downloads/$NAME"
for dir in Chapter_*; do   newname=$(echo "$dir" | sed -E 's/(Chapter[_ ]?|^)([0-9]{1})([^0-9]|$)/\100\2\3/g');   [ "$newname" != "$dir" ] && mv "$dir" "$newname"; done
for dir in Chapter_*; do   newname=$(echo "$dir" | sed -E 's/([^0-9]|^)([0-9]{2})([^0-9]|$)/\10\2\3/g');   [ "$newname" != "$dir" ] && mv "$dir" "$newname"; done
popd
```

## Step 3: Move to Dropbox, Generate HTML

```shell
DEST="/home/shalom/Dropbox/backups/quests, hobbies and entertainment/manhwa"
mv "downloads/$NAME" "${DEST}"
python3 /home/shalom/workspace/download-manwha/generate-manhwa-html/generate_manhwa_html.py "$DEST/$NAME"
```

## Step 4: Edit index.html to add link

Edit the file 
"/home/shalom/Dropbox/backups/quests, hobbies and entertainment/manhwa/index.html"
to add a link to the newly created folder, so it's easy to find.

## Wishlist:

* Mark end of chapter while reading
* Mark chapter as duplicate and decide which one stays

