set(FIREDOG_FILES
./converter.cpp
./matcher.cpp
./rule/rule.cpp
./featurelibrary.cpp
./json/json-schema/json-schema-draft7.json.cpp
./json/json-schema/string-format-check.cpp
./json/json-schema/json-patch.cpp
./json/json-schema/json-uri.cpp
./json/json-schema/json-validator.cpp
./firedog.cpp
)
add_library(FIREDOG ${FIREDOG_FILES})

