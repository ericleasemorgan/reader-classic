<?xml version="1.0"?>

<!-- xml2tsv.xsl - given an XML file of a specific shape, output a TSV file

	 Eric Lease Morgan <emorgan@nd.edu>
	 (c) University of Notre Dame; distributed under a GNU Public License

	 September 5, 2020 - first cut -->
	 

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="text" encoding="UTF-8" />
	<xsl:variable name="lowercase" select="'./'" />
	<xsl:variable name="uppercase" select="'_-'" />

	<xsl:template name="lower">
		<xsl:param name="text"/>
		<xsl:value-of select="translate($text, $lowercase, $uppercase)"/>
	</xsl:template> 
    
	<xsl:template match="/xml">
	
		<!-- header -->
		<xsl:text>author&#09;title&#09;date&#09;abstract&#09;doi&#09;file&#10;</xsl:text>
	
		<!-- each record -->
		<xsl:for-each select='//record'>
	
		<!-- simple bibliographics -->
		<xsl:value-of select='./contributors/authors/author' />
		<xsl:text>&#09;</xsl:text>
		<xsl:value-of select='./titles/title/style' />
		<xsl:text>&#09;</xsl:text>
		<xsl:value-of select='./dates/year/style' />
		<xsl:text>&#09;</xsl:text>
		<xsl:value-of select='./abstract/style' />
		<xsl:text>&#09;</xsl:text>
		<xsl:value-of select='./doi/style' />
		<xsl:text>&#09;</xsl:text>

		<!-- create a file name from the DOI -->
		<xsl:call-template name="lower">
			<xsl:with-param name="text">
				<xsl:value-of select='./doi/style' />
			</xsl:with-param>
		</xsl:call-template>
		<xsl:text>.pdf</xsl:text>

		<!-- end of record -->
		<xsl:text>&#10;</xsl:text>
	
		</xsl:for-each>
	
	</xsl:template>

</xsl:stylesheet>