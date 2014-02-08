#!/usr/bin/python
import varnishhoststatcore,getopt,os,sys
#based on Jurgen Hermanns http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012

def main(opts):
	vhs = varnishhoststatcore.varnishHostStat(opts)
	vhs.execute()

if __name__ == '__main__':
	try:
		opts,args = getopt.getopt(sys.argv[1:],"ajrF:i:w:DP:",["start="])
	except getopt.GetoptError:
		print 'param err'
		sys.exit(2)
	
	d_flag = False
	p_file = False
	for o,a in opts:
		if   o == '-D':
			d_flag = True
		elif o == '-P':
			p_file = a
	if d_flag:
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError, e:
			print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
			sys.exit(1)
		os.chdir("/")
		os.setsid()
		os.umask(0)
		try:
			pid = os.fork()
			if pid > 0:
				if p_file:
					open(p_file,'w').write("%d"%pid)
				sys.exit(0)
		except OSError, e:
			print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
			sys.exit(1)
	main(opts)


