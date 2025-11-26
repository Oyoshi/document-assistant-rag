module.exports = {
    "*/**/*.{js,jsx,ts,tsx}": [
        "npx prettier --write",
        "npx eslint --fix",
    ],
    "*/**/*.{json,css,md}": [
        "npx prettier --write"
    ]
};
