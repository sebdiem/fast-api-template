install:
	uvx pre-commit==4.3.0 install
	cd back && make install
	cd front && pnpm install

pre-commit:
	uvx pre-commit==4.3.0 run --all -v
