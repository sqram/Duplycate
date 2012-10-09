# author: lyrae
# http://none.io

import glib
import gtk
import os
import shutil
from cgi import escape
from sys import exit


# Class that returns a fully built treeview
class NewTree(object):

	def make_tree(self, tab_num = None):
		''' Returns a treeview with columns '''
		self.liststore = gtk.ListStore(str, str, str)
		treeview = gtk.TreeView(self.liststore)
		cell = gtk.CellRendererText()

		if tab_num == 4:
			# 4th tab/tree does not have columns. only one.
			tvcolumn_message = gtk.TreeViewColumn('Message', cell,  markup=0)
			treeview.append_column(tvcolumn_message)

		else:
			tvcolumn_filename = gtk.TreeViewColumn('File/Dir', cell,  markup=0)
			tvcolumn_filepath = gtk.TreeViewColumn('Path', cell,  markup=1)
			tvcolumn_status = gtk.TreeViewColumn('Status', cell, markup=2)

			treeview.append_column(tvcolumn_filename)
			treeview.append_column(tvcolumn_filepath)
			treeview.append_column(tvcolumn_status)

		return treeview


class Duplycate:

	def __init__(self):

		# -- Our window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.set_border_width(10)
		self.window.set_title('Duplycate')
		self.window.set_geometry_hints(self.window, min_width=750, min_height=450)

		# -- Widgets
		# FileChooserDialogs
		self.src_dir_dialog = gtk.FileChooserDialog(
			title="Select source folder",
			action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
		)

		self.dst_dir_dialog = gtk.FileChooserDialog(
			title="Select destination folder",
			action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
		)

		# Butons & checkbuttons
		button_start = gtk.Button('Start')
		button_options = gtk.ToggleButton('Options')
		src_dir = gtk.FileChooserButton(self.src_dir_dialog)
		dst_dir = gtk.FileChooserButton(self.dst_dir_dialog)
		print
		print
		print "*" * 20
		print src_dir.get_uri()
		print dst_dir
		print "*" * 20
		print
		print
		self.unmount_button = gtk.CheckButton("Try to unmount drive when finished?")
		self.unmount_button.set_border_width(10)


		# Notebook & tabs
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_TOP)

		label_1 = gtk.Label('SRC -> DST')
		label_2 = gtk.Label('DST -> SRC')
		label_3 = gtk.Label('Deleted')
		label_4 = gtk.Label('Errors')

		# Tree instances
		self.tree1 = NewTree()
		self.tree2 = NewTree()
		self.tree3 = NewTree()
		self.tree4 = NewTree()

		# Create scrolled windows to hold the treeviews
		sw1 = gtk.ScrolledWindow()
		sw2 = gtk.ScrolledWindow()
		sw3 = gtk.ScrolledWindow()
		sw4 = gtk.ScrolledWindow()

		# Add treeviews to the scrolled windows
		sw1.add(self.tree1.make_tree())
		sw2.add(self.tree2.make_tree())
		sw3.add(self.tree3.make_tree())
		sw4.add(self.tree4.make_tree(4))

		# Notebook pages.
		self.notebook.append_page(sw1, label_1)		# 0. Tab1: src -> dst
		self.notebook.append_page(sw2, label_2)		# 1. Tab2: dst -> src
		self.notebook.append_page(sw3, label_3)		# 2. Tab3: Deleted from dst
		self.notebook.append_page(sw4, label_4)		# 3. Tab4: Errors

		# Frame
		frame = gtk.Frame(' Options')
		frame.set_border_width(20)
		frame.set_shadow_type(gtk.SHADOW_OUT)
		frame.set_label_align(0.03, 0.5)


		# textview
		textview = gtk.TextView()
		textview.set_border_window_size(gtk.TEXT_WINDOW_TOP, 10)
		textview.set_border_window_size(gtk.TEXT_WINDOW_BOTTOM, 10)
		textview.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 10)
		textview.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 10)
		self.textbuffer = textview.get_buffer()

		helptext = """/media/shared/RECYCLER
/media/shared/System Volume Information
/media/shared/stuff/PSDs
/media/shared/$Recycle.Bin"""
		self.textbuffer.set_text(helptext)

		# Progress Bar
		self.p = gtk.ProgressBar()
		self.p.set_text('Ready')
		self.p.set_fraction(1)

		# Status bar
		self.statusbar = gtk.Statusbar()
		self.statusbar.push(0, 'Welcome to Duplycate')

		# Boxes and packing
		hbox_options_1 = gtk.HBox()
		hbox_options_2 = gtk.HBox()
		vbox_options = gtk.VBox()
		hbox = gtk.HBox(spacing=5)
		vbox = gtk.VBox(spacing=10)

		hbox.pack_start(src_dir, 1, 1, 0)
		hbox.pack_start(dst_dir, 1, 1, 0)
		hbox.pack_start(button_options, 0, 0, 1)
		hbox.pack_start(button_start, 0, 1, 0)
		hbox.pack_start(self.p, 0, 1, 0)
		vbox.pack_start(hbox, 0, 0)
		hbox_options_1.pack_start(self.unmount_button, 0, 0, 0)
		hbox_options_2.pack_start(textview)

		#vbox_options.pack_start(hbox_options_1)
		vbox_options.pack_start(hbox_options_1)
		vbox_options.pack_start(gtk.HSeparator())
		vbox_options.pack_start(hbox_options_2)
		frame.add(vbox_options)
		vbox.pack_start(frame)
		vbox.pack_start(textview)
		vbox.pack_start(self.notebook)
		vbox.pack_start(self.statusbar,0 ,0, 0)

		# Bind events
		button_start.connect("clicked", self.start)
		button_options.connect("clicked", self.show_options_area, frame)
		#self.notebook.connect("switch-page", self.test) #TODO make tab labels bold when something logged
		#label_1.set_markup('<span foreground="blue">ff</span>')

		# Show it all
		self.window.add(vbox)
		self.window.show_all()
		frame.hide()

	def show_options_area(self, button, frame):
		if button.get_active() == True:
			frame.show()
		else:
			frame.hide()

	def log(self, tab, tup):
		''' puts text on a column row '''
		tabs = [self.tree1, self.tree2, self.tree3, self.tree4]
		if tab == 3:
			# This is error tab. Tuple has only 1 element (it's actually a string)
			# Because the treestore was build like gtk.TreeStore(str, str, str'), it expects 3 values. Pass those extra
			# values as blanks
			tabs[3].liststore.append((tup, '', ''))
		else:
			filename, filepath, status =  tup
			tabs[tab].liststore.append([escape(filename), escape(filepath), escape(status)])

	# When copying an entire directory structure, make sure
	# its subdirs are skipped if user wants to'
	def _ignore(self, root, contents):
		for d in contents:
			if os.path.join(root, d) in self.skip:
				return d
		return root

	def start(self, e):

		# self.skip is a list of paths user wishes to not copy/check
		buffer_content = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter())
		self.skip = buffer_content.split("\n")
		# Paths cannot end with /
		for index, element in enumerate(self.skip):
			if element:
				if element[-1] == '/':
					self.skip[index] = element[:-1]


		self.p.set_text('Scanning...')

		# each waker is in format ( path, [dirs] [files] )
		self.src_walker = os.walk(self.src_dir_dialog.get_current_folder())
		self.dst_walker = os.walk(self.dst_dir_dialog.get_current_folder())
		print
		print self.src_dir_dialog.get_uri()
		print self.dst_dir_dialog.get_current_folder();
		print
		# bug - if it's not a device (hdd, /), it returns home dir
		import sys
		sys.exit()
		glib.idle_add(self.scan)

	def scan(self):
		try:
			src_root, src_dirs, src_files = self.src_walker.next()
			dst_root, dst_dirs, dst_files = self.dst_walker.next()
			src_dirs.sort()
			dst_dirs.sort()

			# First, we see if any of these directories wish to be skipped. If so, delete it from src_dirs and dst_dirs
			for d in src_dirs[:]:
				if os.path.join(src_root, d) in self.skip:
					src_dirs.remove(d)
					try:
						dst_dirs.remove(d)
					except:
						#print 'could not remove %s from src_dirs' % d
						print('exiting')
						#exit()

			# Folders. Folder that are in dst but not src, will be deleted from dst. Folders that are in src but not in dst,
			# will be copied to dst.
			for folder in dst_dirs[:]:
				if folder not in src_dirs:
					try:
						shutil.rmtree(os.path.join(dst_root, folder))
						self.log(2, (directory, dst_root, 'Deleted %s from dst.' % folder))
						#print 'Deleting %s from dst. Not found in src' % os.path.join(dst_root, folder)
					except:
						#print '*** dint delete ***'
						self.log(3, ('Could not delete %s from dst.' % folder))
					dst_dirs.remove(folder)
					#print 'dst_dirs is now: ', dst_dirs


			# Now copy folders that are in src but not in dst, to dst.
			for directory in src_dirs[:]:
				if directory not in dst_dirs:
					try:
						self.log(0, (directory, src_root, '%s did not exist in destination drive. Copied from src -> dst' % directory))
						shutil.copytree(os.path.join(src_root, directory), os.path.join(dst_root, directory), ignore=self._ignore)

					except:
						self.log(3, ('Could not copy %s to dst.' % os.path.join(src_root, directory)))
						#print '<<< could not copy %s to dst >>>' % directory
						# Delete these folders from src_dirs so we don't go into them
					src_dirs.remove(directory)


			# Files. If a file is in dst but not src, it'll be deleted. If a file is in src and not dst, it will be copied. If a file
			# exists in both places, we check modification date. Older file gets replaced with the newer one. A responsible
			# user should never modify a file in the backup drive. It should always be modifed in the source drive, then
			# copied to the backup drive. In the case a user has modified a file in the dst drive and not the src drive,
			# this program will copy the modified file from dst to src. In case this happens, as a precaution, a copy of
			# src's file will be placed on the desktop.
			for f in dst_files:
				backedup = False
				if f not in src_files:
					try:
						os.unlink(os.path.join(dst_root, f))
						self.log(2, (f, dst_root, 'Deleted %s from dst.' % f))
					except:
						self.log(3, ('Could not delete %s from dst.' % os.path.join(dst_root, f)))
				else:

					try:
						# This file is in the src folder as well. Check modification dates
						  src_statinfo = os.stat(os.path.join(src_root, f))
						  dst_statinfo = os.stat(os.path.join(dst_root, f))
						  if abs(src_statinfo.st_mtime - dst_statinfo.st_mtime) < .0001:
							  # They have the same modification date. do nothing
							  pass
						  elif src_statinfo.st_mtime < dst_statinfo.st_mtime:
							  backup_dir = os.path.expanduser('~/Desktop/duplycate_backup/')
							  #Before copying over, backup this file
							  #TODO make sure a file with he same name does not exist in backup_dir
							  if not os.path.exists(backup_dir):
								  os.mkdir(backup_dir)
							  try:
								  shutil.copy2(os.path.join(src_root, f), os.path.join(backup_dir, f))
								  backedup = True
							  except:
								  # Take no risks. if file could not be backed up before moving from dst -> src,
								  # exit the program...better than losing a file.
								  print "Exiting. check like 307";
								  exit()


							  # Now that the file is backed up, from from dst -> src
							  if backedup == True:
								  try:
									  shutil.copy2( os.path.join(dst_root, f), os.path.join(src_root, f) )
								  except OSError as error:
									  p = os.path.join(dst_root, f)
									  if error.errno == 1:
										  self.log(1, (f, dst_root, '%s is newer in dst. Copied from dst -> src' % f))
										  self.log( 3, ('Copied %s from dst -> src, but did not copy metadata. Probably 2 different FS.' % p))
									  else:
										  self.log( 3, ('Could not copy %s from dst to src. Try running as root.' % p ))
									  os.unlink(os.path.join(backup_dir, f))

						  elif src_statinfo.st_mtime > dst_statinfo.st_mtime:
							  try:
								  shutil.copy2(os.path.join(src_root, f), os.path.join(dst_root, f))
								  self.log(0, (f, src_root, '%s is newer in src. Copied from src -> dst' % f))
							  except:
								  self.log(3, ('Could not copy %s from src to dst.' % os.path.join(dst_root, f)))
					except:
						print "something bad"

			# Now copy files that are in src but not in dst, to dst.
			for f in src_files:
				if f not in dst_files:
					try:
						shutil.copy2(os.path.join(src_root, f), os.path.join(dst_root, f))
						self.log(0, (f, src_root, '%s is newer in src. Copied from src -> dst' % f))
					except:
						self.log(3, ('Could not copy %s from src to dst.' % os.path.join(dst_root, f)))


			# Pulse progress bar
			self.p.pulse()
			#print '-'*50
			return True
		except StopIteration:
			if self.unmount_button.get_active() == True:
				import subprocess
				try:
					subprocess.Popen(['umount', self.dst_dir_dialog.get_current_folder()])
					self.statusbar.push(0, 'Finished. Could not unmount %s.' % self.dst_dir_dialog.get_current_folder())
				except:
					self.statusbar.push(0, 'Finished and successfully unmounted %s.' % self.dst_dir_dialog.get_current_folder())
			else:
				self.statusbar.push(0, 'Finished.')
			self.p.set_text('Done.')
			return False

	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False


def main():
	gtk.main()
	return 0

if __name__ == "__main__":
	app = Duplycate()
	main()

'''david3432:stoney
/media/shared/stuff/PSDs
/media/shared/RECYCLER
/media/shared/System Volume Information
'''



