ZIPFILE=${1:-$(ls -rt *.zip | tail -1)}
unzip -o ${ZIPFILE}
git add $(unzip -l ${ZIPFILE} | tail -n +4 | head -n -2 | awk '{print $(NF)}')
CM=$(unzip -l ${ZIPFILE} | tail -n +4 | head -n -2 | awk '/COMMIT_MESSAGE/ {print $(NF)}')

if [[ -z "$CM" ]]
then
    echo No commit message found in the zip file. Exiting.
    exit 1
fi 

cat ${CM}
git commit -a -F ${CM} && git push
./create_git_archive.sh
# ./run.sh
