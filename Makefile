install:
	uvx pre-commit==4.3.0 install
	cd back && make install
	if [ -d front ]; then cd front && pnpm install; fi

pre-commit:
	uvx pre-commit==4.3.0 run --all -v
