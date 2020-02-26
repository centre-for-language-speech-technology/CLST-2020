if [ $# -eq 2 ]; then
	if [ $1 == "utf-16be" ] || [ $1 == "utf-16le" ]; then
		from_encoding=$1
		file=$2
	elif [ $2 == "utf-16be" ] || [ $2 == "utf-16le" ]; then
		from_encoding=$2
		file=$1
	else
		echo "Error: Wrong arguments"
else
	echo "Error: Need two arguments. from_encoding and file"

iconv -f ${from_encoding} -t utf-8 "$file" -o "${file}-converted"
mv "${file}-converted" "$file"
sed -i 's/^\xEF\xBB\xBF//' "$file"
echo "Converted $file from ${from_encoding} encoding to utf-8 ... "