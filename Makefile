.PHONY: all clean

all:
	$(MAKE) -C lib/thea all

clean:
	$(MAKE) -C lib/thea clean
	rm -rf lib/thea/*.pyc
