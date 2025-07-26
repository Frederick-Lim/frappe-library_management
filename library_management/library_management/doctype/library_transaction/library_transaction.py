# Copyright (c) 2025, Frederick Lim and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus


class LibraryTransaction(Document):
	def before_submit(self):
		if self.type == "Issue":
			self.validate_issue()
			# set the article status to 'Issued'
			article = frappe.get_doc("Article", self.article)
			article.status = "Issued"
			article.save()

		elif self.type == "Return":
			self.validate_return()
			# set the article status to 'Available'
			article = frappe.get_doc("Article", self.article)
			article.status = "Available"
			article.save()

	def validate_issue(self):
		# Validate membership before issuing an article
		self.validate_membership()

		# Get the article document based on the article name in the transaction
		article = frappe.get_doc("Article", self.article)
		# Check if the article is already issued
		if article.status == "Issued":
			frappe.throw("This article is already issued")
			
	def validate_return(self):
		# Validate membership before returning an article
		self.validate_membership()

		# Get the article document based on the article name in the transaction
		article = frappe.get_doc("Article", self.article)
		# Check if the article is available for return
		if article.status == "Available":
			frappe.throw("This article cannot be returned as it is not issued")

	# Checks whether the maximum limit is reached when an Article is Issued
	def validate_maximum_limit(self):
		max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
		count = frappe.db.count(
			"Library Transaction",
			{
				"library_member": self.library_member,
				"type": "Issue",
				"docstatus": DocStatus.submitted(),
			},
		)
		if count >= max_articles:
			frappe.throw(f"The maximum number of articles that can be issued is {max_articles}")

	def validate_membership(self):
		valid_membership = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": DocStatus.submitted(),
				"from_date": ("<", self.date),
				"to_date": (">", self.date),
			},
		)
		if not valid_membership:
			frappe.throw("The member does not hava a valid membership")